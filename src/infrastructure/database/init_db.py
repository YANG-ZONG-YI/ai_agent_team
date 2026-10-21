from sqlalchemy import text
from src.infrastructure.database.models import Base, engine

def init_database():
    """初始化資料庫擴充套件與所有資料表"""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)
    print("【Database Initialized】All tables & vector extension ready.")

if __name__ == "__main__":
    init_database()
