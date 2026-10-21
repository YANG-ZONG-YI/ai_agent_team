import pytest
from src.infrastructure.adapters.notion_adapter import NotionAdapter, NotionItemDTO

def test_parse_notion_query_response_to_dto():
    adapter = NotionAdapter(api_key="fake-key", database_id="fake-db")
    
    # 模擬 Notion API 回傳之複雜巢狀 JSON
    mock_notion_response = {
        "results": [
            {
                "id": "page-uuid-111",
                "properties": {
                    "Name": {
                        "title": [{"plain_text": "AI 短影音自動化實戰"}]
                    },
                    "Prompt": {
                        "rich_text": [{"plain_text": "以實例展示管線運作流程"}]
                    },
                    "Status": {
                        "select": {"name": "待製作"}
                    }
                }
            }
        ]
    }
    
    items = adapter.parse_query_results(mock_notion_response)
    
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, NotionItemDTO)
    assert item.page_id == "page-uuid-111"
    assert item.title == "AI 短影音自動化實戰"
    assert item.prompt == "以實例展示管線運作流程"
    assert item.status == "待製作"

def test_format_notion_update_payload():
    adapter = NotionAdapter(api_key="fake-key", database_id="fake-db")
    payload = adapter.build_update_payload(
        status="待發布",
        preview_url="/videos/video-123.mp4"
    )
    
    assert payload["properties"]["Status"]["select"]["name"] == "待發布"
    assert payload["properties"]["Preview_URL"]["url"] == "/videos/video-123.mp4"
