import pytest
from uuid import uuid4
import numpy as np
from src.infrastructure.database.models import SessionLocal
from src.infrastructure.database.script_repository import ScriptKnowledgeRepository

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def generate_mock_vector(seed: float = 1.0) -> list[float]:
    """生成 1536 維度長度的單位向量"""
    vec = np.zeros(1536)
    vec[0] = seed
    vec[1] = 1.0 - seed
    norm = np.linalg.norm(vec)
    return (vec / norm).tolist()

def test_script_knowledge_repository_duplicate_detection(db_session):
    from src.infrastructure.database.models import VideoJobModel
    repo = ScriptKnowledgeRepository(db_session)
    
    # 先建立關聯的 Job
    job = VideoJobModel(
        notion_page_id=f"test-page-{uuid4()}",
        title="AI Agent 開發指南",
        prompt="測試提示詞"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    
    # 建立第一筆劇本與向量
    base_vec = generate_mock_vector(seed=1.0)
    repo.save_script_embedding(
        job_id=job.id,
        script_content="【短影音第一集】AI Agent 開發指南，五分鐘搞懂全流程",
        embedding=base_vec
    )
    
    # 測試 1：查詢完全相同或極度相似的向量 (Cosine Similarity ~ 1.0)
    similar_vec = generate_mock_vector(seed=0.99) # 極度相似
    is_dup, max_sim = repo.check_duplicate(similar_vec, threshold=0.85)
    assert is_dup is True
    assert max_sim >= 0.85
    
    # 測試 2：查詢差異極大的向量 (Cosine Similarity ~ 0.0)
    orthogonal_vec = np.zeros(1536)
    orthogonal_vec[100] = 1.0
    is_dup2, max_sim2 = repo.check_duplicate(orthogonal_vec.tolist(), threshold=0.85)
    assert is_dup2 is False
    assert max_sim2 < 0.85
