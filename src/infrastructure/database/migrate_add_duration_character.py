from sqlalchemy import text
from src.infrastructure.database.models import engine

def migrate():
    print("Starting migration for target_duration and character_id...")
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE video_pipeline_jobs ADD COLUMN IF NOT EXISTS target_duration INTEGER NOT NULL DEFAULT 30;"))
        conn.execute(text("ALTER TABLE video_pipeline_jobs ADD COLUMN IF NOT EXISTS character_id VARCHAR(64) NOT NULL DEFAULT 'default_anchor';"))
        conn.commit()
    print("Migration finished successfully!")

if __name__ == "__main__":
    migrate()
