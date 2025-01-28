from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from . import config
from .downloader import InsizeDownloader
from .parser import ExcelParser
from .database import Database
from .shopify_client import ShopifyClient

class SyncManager:
    def __init__(self):
        self.downloader = InsizeDownloader()
        self.database = Database()
        self.shopify_client = ShopifyClient()
        
    def setup(self):
        """Initialize connections and create tables"""
        try:
            self.database.connect()
            self.database.create_tables()
        except Exception as e:
            logger.error(f"Setup failed: {str(e)}")
            raise
            
    def cleanup(self):
        """Close connections"""
        try:
            self.database.close()
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            
    def sync(self):
        """Main synchronization logic"""
        logger.info("Starting synchronization")
        excel_file = None
        
        try:
            # Download Excel file
            excel_file = self.downloader.download_excel()
            if not excel_file:
                raise Exception("Failed to download Excel file")
                
            # Parse Excel file
            parser = ExcelParser(excel_file)
            products = parser.parse()
            
            if not products:
                raise Exception("No products found in Excel file")
                
            # Update database
            self.database.upsert_products(products)
            
            # Update Shopify
            updated, added = self.shopify_client.update_products(products)
            
            # Log success
            self.database.log_sync(
                products_updated=updated,
                products_added=added,
                status="success"
            )
            
            logger.info(f"Sync completed: {updated} updated, {added} added")
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Sync failed: {error_message}")
            
            # Log failure
            try:
                self.database.log_sync(
                    products_updated=0,
                    products_added=0,
                    status="failed",
                    error_message=error_message
                )
            except Exception as log_error:
                logger.error(f"Failed to log sync failure: {str(log_error)}")
                
        finally:
            # Cleanup temporary file
            if excel_file:
                self.downloader.cleanup(excel_file)
                
def run_scheduler():
    """Run the scheduler"""
    try:
        manager = SyncManager()
        manager.setup()
        
        scheduler = BlockingScheduler()
        
        # Add jobs for both sync times
        for sync_time in config.SYNC_TIMES:
            if sync_time:
                hour, minute = map(int, sync_time.split(':'))
                trigger = CronTrigger(hour=hour, minute=minute)
                
                scheduler.add_job(
                    manager.sync,
                    trigger=trigger,
                    name=f"sync_{hour}_{minute}"
                )
                
                logger.info(f"Scheduled sync for {hour:02d}:{minute:02d}")
                
        logger.info("Starting scheduler")
        scheduler.start()
        
    except Exception as e:
        logger.error(f"Scheduler failed: {str(e)}")
        raise
    finally:
        manager.cleanup()
        
if __name__ == "__main__":
    run_scheduler() 