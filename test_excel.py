from src.downloader import InsizeDownloader
from src.parser import ExcelParser
import pandas as pd
from loguru import logger

def test_download_and_examine():
    downloader = InsizeDownloader()
    try:
        # Download Excel file
        excel_file = downloader.download_excel()
        if not excel_file:
            logger.error("Failed to download Excel file")
            return

        # Read and examine Excel structure
        df = pd.read_excel(excel_file)
        
        # Print column names
        logger.info("Excel columns:")
        for col in df.columns:
            logger.info(f"- {col}")
            
        # Print first row as sample
        logger.info("\nFirst row sample:")
        for col in df.columns:
            logger.info(f"{col}: {df.iloc[0][col]}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if excel_file:
            downloader.cleanup(excel_file)

if __name__ == "__main__":
    test_download_and_examine() 