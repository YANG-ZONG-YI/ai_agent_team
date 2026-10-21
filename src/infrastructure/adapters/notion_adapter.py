from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import httpx

@dataclass
class NotionItemDTO:
    """Notion 純淨數據傳輸物件 (DTO)"""
    page_id: str
    title: str
    prompt: str
    status: str

class NotionAdapter:
    """
    Notion API 防腐層適配器 (Anti-Corruption Layer)
    隔離 Notion 複雜巢狀 JSON 結構，提供領域層純淨資料
    """

    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        self.api_key = api_key or ""
        self.database_id = database_id or ""
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.NOTION_VERSION,
            "Content-Type": "application/json"
        }

    def parse_query_results(self, response_data: Dict[str, Any]) -> List[NotionItemDTO]:
        """將 Notion 原始查詢結果轉譯為純淨 DTO 清單"""
        items: List[NotionItemDTO] = []
        for page in response_data.get("results", []):
            page_id = page.get("id", "")
            props = page.get("properties", {})
            
            # 解析標題 (Name)
            title = ""
            name_prop = props.get("Name", {}).get("title", [])
            if name_prop:
                title = name_prop[0].get("plain_text", "")

            # 解析提示詞 (Prompt)
            prompt = ""
            prompt_prop = props.get("Prompt", {}).get("rich_text", [])
            if prompt_prop:
                prompt = prompt_prop[0].get("plain_text", "")

            # 解析狀態 (Status)
            status = ""
            status_prop = props.get("Status", {}).get("select")
            if status_prop:
                status = status_prop.get("name", "")

            items.append(NotionItemDTO(
                page_id=page_id,
                title=title,
                prompt=prompt,
                status=status
            ))
        return items

    def build_update_payload(
        self,
        status: Optional[str] = None,
        preview_url: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """建立更新 Notion Page 屬性之 Payload"""
        properties: Dict[str, Any] = {}
        
        if status:
            properties["Status"] = {"select": {"name": status}}
            
        if preview_url:
            properties["Preview_URL"] = {"url": preview_url}
            
        if error_message:
            properties["Error_Log"] = {
                "rich_text": [{"text": {"content": error_message[:2000]}}]
            }
            
        return {"properties": properties}

    async def fetch_pending_jobs(self) -> List[NotionItemDTO]:
        """查詢狀態為「待製作」的 Notion 頁面"""
        if not self.api_key or not self.database_id:
            return []
            
        url = f"{self.BASE_URL}/databases/{self.database_id}/query"
        payload = {
            "filter": {
                "property": "Status",
                "select": {
                    "equals": "待製作"
                }
            }
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=self.headers, json=payload, timeout=10.0)
            if resp.status_code == 200:
                return self.parse_query_results(resp.json())
        return []

    async def update_page(self, page_id: str, payload: Dict[str, Any]) -> bool:
        """更新指定 Notion 頁面屬性"""
        if not self.api_key:
            return True # 測試/離線模式直接回傳成功
            
        url = f"{self.BASE_URL}/pages/{page_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.patch(url, headers=self.headers, json=payload, timeout=10.0)
            return resp.status_code == 200
