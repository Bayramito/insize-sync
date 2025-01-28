from src.csv_exporter import export_to_shopify_csv
from loguru import logger

def test_csv_export():
    """Test CSV export functionality"""
    try:
        logger.info("Starting CSV export test...")
        # Her dosyada 1000 ürün olacak şekilde export et
        export_to_shopify_csv(batch_size=1000, output_dir='shopify_exports')
        logger.success("CSV export test completed successfully")
    except Exception as e:
        logger.error(f"CSV export test failed: {str(e)}")
        raise

if __name__ == '__main__':
    test_csv_export() 