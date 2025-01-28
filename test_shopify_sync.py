from src.shopify_sync import ShopifySync
from loguru import logger
import sys

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

def test_shopify_sync():
    """Test syncing products to Shopify"""
    logger.info("Starting Shopify sync test...")
    
    try:
        syncer = ShopifySync()
        syncer.sync_products()
        logger.success("Shopify sync test completed successfully!")
        
    except Exception as e:
        logger.error(f"Shopify sync test failed: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("=== Shopify Sync Test Starting ===")
    test_shopify_sync()
    logger.info("=== Shopify Sync Test Complete ===") 