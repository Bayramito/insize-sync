from src.database import Database
from src.parser import ExcelParser
from src.downloader import InsizeDownloader
from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

def test_sync():
    """Test syncing products to database"""
    logger.info("Starting sync test...")
    
    try:
        # Download Excel file
        logger.info("Downloading Excel file...")
        downloader = InsizeDownloader()
        file_path = downloader.download_excel()
        
        # Parse Excel file
        logger.info("Parsing Excel file...")
        parser = ExcelParser(file_path)
        products = parser.parse()
        logger.info(f"Parsed {len(products)} products")
        
        # Connect to database
        logger.info("Connecting to database...")
        db = Database()
        db.connect()
        
        # Create tables if they don't exist
        logger.info("Creating tables...")
        db.create_tables()
        
        # Insert products
        logger.info("Inserting products...")
        db.upsert_products(products)
        
        # Verify insertion
        logger.info("Verifying insertion...")
        df = db.get_all_products()
        logger.info(f"Total products in database: {len(df)}")
        
        # Log sync
        logger.info("Logging sync...")
        db.log_sync(
            products_updated=len(products),
            products_added=len(products),
            status="SUCCESS"
        )
        
        logger.success("Sync test completed successfully!")
        
    except Exception as e:
        logger.error(f"Sync test failed: {str(e)}")
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        if 'downloader' in locals():
            downloader.cleanup(file_path)
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    logger.info("=== Sync Test Starting ===")
    test_sync()
    logger.info("=== Sync Test Complete ===") 