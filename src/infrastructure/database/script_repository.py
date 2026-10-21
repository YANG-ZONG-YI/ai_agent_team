from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from src.infrastructure.database.models import ScriptEmbeddingModel

class ScriptKnowledgeRepository:
    """劇本知識庫與向量檢索持久化 Repository"""

    def __init__(self, db_session: Session):
        self.session = db_session

    def save_script_embedding(
        self,
        job_id: Optional[UUID],
        script_content: str,
        embedding: list[float],
        similarity_threshold: float = 0.85
    ) -> ScriptEmbeddingModel:
        """持久化儲存劇本內容與對應的向量特徵"""
        record = ScriptEmbeddingModel(
            job_id=job_id,
            script_content=script_content,
            embedding=embedding,
            similarity_score_threshold=similarity_threshold
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def check_duplicate(
        self,
        embedding: list[float],
        threshold: float = 0.85
    ) -> Tuple[bool, float]:
        """
        利用 pgvector 餘弦距離檢索歷史劇本庫，判斷是否達到重複閥值
        回傳: (是否重複, 最高相似度分數)
        餘弦相似度 = 1 - cosine_distance
        """
        # 利用 pgvector 的 cosine_distance 運算子
        query = (
            self.session.query(
                ScriptEmbeddingModel,
                (1 - ScriptEmbeddingModel.embedding.cosine_distance(embedding)).label("similarity")
            )
            .order_by(ScriptEmbeddingModel.embedding.cosine_distance(embedding))
            .limit(1)
        )
        
        result = query.first()
        if not result:
            return False, 0.0

        record, similarity = result
        sim_score = float(similarity)
        is_dup = sim_score >= threshold
        return is_dup, sim_score
