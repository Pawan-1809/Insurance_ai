from app.db.database import engine, Base
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database by creating all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")

if __name__ == "__main__":
    init_database() 