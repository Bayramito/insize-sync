from src.database import Database
from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

def test_connection():
    """Test database connection and table creation"""
    logger.info("Starting database connection test...")
    db = Database()
    try:
        # Test connection
        logger.info("Attempting to connect to database...")
        db.connect()
        logger.success("Database connection successful!")
        
        # Test table creation
        logger.info("Attempting to create tables...")
        db.create_tables()
        logger.success("Tables created successfully!")
        
        # Test if tables exist
        db.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = db.cursor.fetchall()
        logger.info(f"Existing tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        logger.info("Closing database connection...")
        db.close()
        logger.info("Test completed.")

if __name__ == "__main__":
    logger.info("=== Database Test Starting ===")
    test_connection()
    logger.info("=== Database Test Complete ===") 