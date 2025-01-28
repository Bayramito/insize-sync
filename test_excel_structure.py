import pandas as pd
from loguru import logger
import sys
from src.downloader import InsizeDownloader

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG"
)

def test_excel_structure():
    """Test the Excel file structure"""
    try:
        # Download the Excel file
        logger.info("Downloading Excel file...")
        downloader = InsizeDownloader()
        file_path = downloader.download_excel()
        
        # Read the Excel file
        logger.info(f"Reading Excel file: {file_path}")
        df = pd.read_excel(file_path)
        
        # Log DataFrame info
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"Column names: {df.columns.tolist()}")
        
        # Log first row
        logger.info("First row:")
        logger.info(df.iloc[0].to_dict())
        
        # Log null value counts
        logger.info("Null value counts:")
        logger.info(df.isnull().sum())
        
        # Log unique values in key columns
        logger.info("Unique values in 'Unnamed: 4' (availability):")
        logger.info(df['Unnamed: 4'].unique())
        
        logger.info("Unique values in 'Unnamed: 16' (price):")
        logger.info(df['Unnamed: 16'].unique())
        
        # Cleanup
        logger.info("Cleaning up...")
        downloader.cleanup(file_path)
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
        
if __name__ == "__main__":
    logger.info("=== Testing Excel Structure ===")
    test_excel_structure()
    logger.info("=== Excel Structure Test Complete ===") 