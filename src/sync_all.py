from loguru import logger
from .csv_exporter import export_to_shopify_csv
import os
import shutil

def sync_all():
    """
    Veritabanındaki ürünleri tek bir CSV dosyasına export eder.
    """
    try:
        logger.info("CSV export işlemi başlatılıyor...")
        
        # Önce shopify_exports klasörünü temizle
        export_dir = 'shopify_exports'
        if os.path.exists(export_dir):
            logger.info(f"{export_dir} klasörü temizleniyor...")
            shutil.rmtree(export_dir)
        os.makedirs(export_dir, exist_ok=True)
        logger.info(f"{export_dir} klasörü hazırlandı.")
        
        # CSV Export
        export_to_shopify_csv(output_dir='shopify_exports')
        
        logger.success("CSV export işlemi tamamlandı!")
        logger.info("Oluşturulan CSV dosyası 'shopify_exports' klasöründe bulunabilir.")
        logger.info("Bu dosyayı Shopify admin panelinden manuel olarak import edebilirsiniz.")
            
    except Exception as e:
        logger.error(f"CSV export hatası: {str(e)}")
        raise

if __name__ == '__main__':
    sync_all() 