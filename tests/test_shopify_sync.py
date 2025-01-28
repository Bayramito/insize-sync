import sys
from loguru import logger
from src.shopify_sync import ShopifySync

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

def test_shopify_sync(is_initial_load: bool = False):
    """Test Shopify product synchronization"""
    try:
        logger.info("Starting Shopify sync test...")
        sync = ShopifySync()
        
        if is_initial_load:
            logger.info("Running initial bulk load of all products...")
            sync.sync_products(is_initial_load=True)
        else:
            logger.info("Running incremental sync of modified products...")
            sync.sync_products(is_initial_load=False)
            
        logger.success("Shopify sync test completed successfully")
        
    except Exception as e:
        logger.error(f"Shopify sync test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Check if this is an initial load
    is_initial = len(sys.argv) > 1 and sys.argv[1] == "--initial"
    test_shopify_sync(is_initial_load=is_initial) 