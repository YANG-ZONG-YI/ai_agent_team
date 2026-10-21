import os
from typing import Optional, Generator
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.infrastructure.database.models import SessionLocal
from src.infrastructure.database.job_repository import SqlAlchemyJobRepository
from src.infrastructure.queue.dispatcher import CeleryQueueDispatcher
from src.infrastructure.adapters.notion_adapter import NotionAdapter
from src.application.ports import IQueueDispatcher
from src.domain.repositories import IJobRepository
from src.application.use_cases.create_video_job import (
    CreateVideoJobUseCase, CreateVideoJobInput
)
from src.application.use_cases.sync_preview import (
    SyncPreviewUseCase, SyncPreviewInput, DomainNotFoundError, DomainValidationError
)

app = FastAPI(
    title="Video Automation Pipeline API",
    description="自動化影音生成與多平台分發管線服務 (DDD & TDD 重構版)",
    version="2.0.0"
)

from uuid import uuid4
from starlette.requests import Request
from starlette.responses import Response
from src.infrastructure.observability.logging import trace_id_ctx, setup_logger

logger = setup_logger("api")

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id", uuid4().hex)
    token = trace_id_ctx.set(trace_id)
    try:
        response: Response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
    finally:
        trace_id_ctx.reset(token)

base_storage = os.getenv("VIDEO_STORAGE_PATH", "/app/storage")
projects_dir = os.path.join(base_storage, "projects")
shared_dir = os.path.join(base_storage, "shared")
system_temp_dir = os.path.join(base_storage, "temp")

os.makedirs(projects_dir, exist_ok=True)
os.makedirs(shared_dir, exist_ok=True)
os.makedirs(system_temp_dir, exist_ok=True)

# 掛載多專案工作區靜態資產中心
app.mount("/projects", StaticFiles(directory=projects_dir), name="projects")

# Pydantic 請求模型
class NotionWebhookPayload(BaseModel):
    page_id: str
    title: str
    prompt: str
    target_duration: Optional[int] = 30
    character_id: Optional[str] = "default_anchor"

class SyncPreviewPayload(BaseModel):
    job_id: str

# 依賴注入工廠 (Dependency Injection)
def get_db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_job_repository(session: Session = Depends(get_db_session)) -> IJobRepository:
    return SqlAlchemyJobRepository(session)

def get_queue_dispatcher() -> IQueueDispatcher:
    return CeleryQueueDispatcher()

def get_create_job_use_case(
    repository: IJobRepository = Depends(get_job_repository),
    dispatcher: IQueueDispatcher = Depends(get_queue_dispatcher)
) -> CreateVideoJobUseCase:
    return CreateVideoJobUseCase(repository, dispatcher)

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "video-automation-pipeline",
        "storage": "mounted"
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to Video Automation Pipeline",
        "docs": "/docs"
    }

@app.post("/api/v1/notion/poll")
async def poll_notion_tasks(
    use_case: CreateVideoJobUseCase = Depends(get_create_job_use_case)
):
    """輪詢 Notion 資料庫中「待製作」的項目並批次建立管線任務"""
    api_key = os.getenv("NOTION_API_KEY", "")
    database_id = os.getenv("NOTION_DATABASE_ID", "")
    adapter = NotionAdapter(api_key=api_key, database_id=database_id)
    
    pending_items = await adapter.fetch_pending_jobs()
    queued_jobs = []
    
    for item in pending_items:
        input_dto = CreateVideoJobInput(
            notion_page_id=item.page_id,
            title=item.title,
            prompt=item.prompt,
            target_duration=30,
            character_id="default_anchor"
        )
        res = use_case.execute(input_dto)
        queued_jobs.append(res.job_id)
            
    return {
        "status": "success",
        "polled_count": len(pending_items),
        "queued_jobs": queued_jobs
    }

@app.post("/api/v1/notion/webhook")
async def notion_webhook_receiver(
    payload: NotionWebhookPayload,
    use_case: CreateVideoJobUseCase = Depends(get_create_job_use_case)
):
    """接收 Notion Webhook 事件並即時建立管線任務 (透過 UseCase)"""
    input_dto = CreateVideoJobInput(
        notion_page_id=payload.page_id,
        title=payload.title,
        prompt=payload.prompt,
        target_duration=payload.target_duration or 30,
        character_id=payload.character_id or "default_anchor"
    )
    result = use_case.execute(input_dto)
    return {
        "status": result.status,
        "job_id": result.job_id,
        "title": result.title
    }

@app.post("/api/v1/notion/sync-preview")
async def sync_preview_to_notion(
    payload: SyncPreviewPayload,
    repository: IJobRepository = Depends(get_job_repository)
):
    """手動或事件觸發將成片預覽 URL 回填至 Notion (透過 UseCase)"""
    adapter = NotionAdapter(
        api_key=os.getenv("NOTION_API_KEY", ""),
        database_id=os.getenv("NOTION_DATABASE_ID", "")
    )
    use_case = SyncPreviewUseCase(repository=repository, notion_adapter=adapter)
    try:
        result = await use_case.execute(SyncPreviewInput(job_id=payload.job_id))
        return {
            "status": result.status,
            "notion_page_id": result.notion_page_id,
            "preview_url": result.preview_url
        }
    except DomainNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
