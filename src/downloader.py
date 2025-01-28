import requests
from loguru import logger
from typing import Optional
import tempfile
import os
from . import config

class InsizeDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.login_url = "https://eshop.insize-eu.com/documentacion.php"
        
    def login(self) -> bool:
        """Login to Insize website"""
        try:
            data = {
                "username": config.INSIZE_USERNAME,
                "password": config.INSIZE_PASSWORD
            }
            
            response = self.session.post(self.login_url, data=data)
            response.raise_for_status()
            
            # Check if login was successful (you might need to adjust this based on the actual response)
            if "error" in response.text.lower():
                logger.error("Login failed")
                return False
                
            logger.info("Successfully logged in to Insize")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
            
    def download_excel(self) -> Optional[str]:
        """Download the Excel file and return the path to the temporary file"""
        try:
            if not self.login():
                return None
                
            response = self.session.get(config.INSIZE_EXCEL_URL)
            response.raise_for_status()
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            temp_file.write(response.content)
            temp_file.close()
            
            logger.info(f"Excel file downloaded successfully to {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Failed to download Excel file: {str(e)}")
            return None
            
    def cleanup(self, file_path: str):
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}") 