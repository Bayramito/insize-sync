from loguru import logger
import sys
from src.downloader import InsizeDownloader
from src.parser import ExcelParser

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

def test_parser():
    try:
        # Download the file
        logger.info("Downloading Excel file...")
        downloader = InsizeDownloader()
        file_path = downloader.download_excel()
        if not file_path:
            logger.error("Failed to download Excel file")
            return
            
        logger.info(f"File downloaded to: {file_path}")
        
        # Parse the file
        logger.info("Parsing Excel file...")
        parser = ExcelParser(file_path)
        products = parser.parse()
        
        # Log results
        logger.info(f"Successfully parsed {len(products)} products")
        
        # Log sample products
        if products:
            logger.info("Sample products:")
            for i, product in enumerate(products[:3], 1):
                logger.info(f"\nProduct {i}:")
                for key, value in product.items():
                    logger.info(f"{key}: {value}")
                    
        # Clean up
        logger.info("Cleaning up...")
        downloader.cleanup(file_path)
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("=== Starting Parser Test ===")
    test_parser()
    logger.info("=== Parser Test Complete ===") 