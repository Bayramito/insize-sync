import pandas as pd
from loguru import logger
from .database import Database
import os
import math

def export_to_shopify_csv(batch_size: int = 1000, output_dir: str = 'shopify_exports'):
    """
    Veritabanındaki ürünleri Shopify CSV formatına dönüştürür ve batch_size kadar ürün içeren
    birden fazla CSV dosyası oluşturur
    """
    try:
        # Çıktı klasörünü oluştur
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Veritabanına bağlan ve ürünleri al
        db = Database()
        db.connect()
        products_df = db.get_all_products()
        
        # Resim URL'si olan ürünleri filtrele
        products_df = products_df[products_df['image_url'].notna() & (products_df['image_url'] != '')]
        
        total_products = len(products_df)
        total_batches = math.ceil(total_products / batch_size)
        
        logger.info(f"Toplam {total_products} ürün (resmi olan), {total_batches} parça halinde export edilecek")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, total_products)
            
            # Bu batch için ürünleri al
            batch_products = products_df.iloc[start_idx:end_idx]
            
            # Shopify CSV formatına dönüştür
            shopify_data = []
            
            for _, product in batch_products.iterrows():
                # Resim URL'sini kontrol et
                if not product['image_url'] or pd.isna(product['image_url']):
                    continue
                    
                shopify_product = {
                    'Handle': product['sku'].lower().replace(' ', '-'),  # URL-friendly handle
                    'Title': product['title'] or f"INSIZE {product['sku']}",
                    'Body (HTML)': product['description'] or '',
                    'Vendor': 'INSIZE',
                    'Type': 'Tools & Equipment',  # Shopify standart kategori
                    'Tags': f"insize, measuring tools, {product['category'] or ''}, {product['subcategory'] or ''}",
                    'Published': 'TRUE' if product['availability'].lower() == 'in stock' else 'FALSE',
                    'Option1 Name': 'Title',
                    'Option1 Value': 'Default Title',
                    'Variant SKU': product['sku'],
                    'Variant Inventory Tracker': 'shopify',
                    'Variant Inventory Qty': '100' if product['availability'].lower() == 'in stock' else '0',
                    'Variant Inventory Policy': 'deny',
                    'Variant Fulfillment Service': 'manual',
                    'Variant Price': str(product['price'] or 0),
                    'Variant Compare At Price': str(product['original_price']) if product['original_price'] else '',
                    'Variant Requires Shipping': 'TRUE',
                    'Variant Taxable': 'TRUE',
                    'Image Src': product['image_url'],
                    'Image Position': '1',
                    'Status': 'active' if product['availability'].lower() == 'in stock' else 'draft',
                    'SEO Title': f"INSIZE {product['sku']} - {product['title']}"[:70] if product['title'] else f"INSIZE {product['sku']}",
                    'SEO Description': product['description'][:320] if product['description'] else '',
                    # Metafields as custom fields
                    'Custom Field [custom.range]': product['range'] or '',
                    'Custom Field [custom.reading]': product['reading'] or '',
                    'Custom Field [custom.family]': product['family'] or '',
                    'Custom Field [custom.weight]': product['weight'] or '',
                    'Custom Field [custom.dimensions]': product['dimensions'] or ''
                }
                shopify_data.append(shopify_product)
            
            if not shopify_data:
                logger.warning(f"Batch {batch_num + 1} boş, atlıyoruz")
                continue
                
            # Bu batch için CSV dosyasını oluştur
            output_file = os.path.join(output_dir, f'shopify_products_batch_{batch_num + 1}_of_{total_batches}.csv')
            shopify_df = pd.DataFrame(shopify_data)
            shopify_df.to_csv(output_file, index=False, encoding='utf-8')
            
            logger.info(f"Batch {batch_num + 1}/{total_batches}: {len(shopify_data)} ürün {output_file} dosyasına kaydedildi")
        
        logger.success(f"Toplam {total_products} ürün {total_batches} parça halinde {output_dir} klasörüne kaydedildi")
        
    except Exception as e:
        logger.error(f"CSV export hatası: {str(e)}")
        raise
    finally:
        if 'db' in locals():
            db.close()

if __name__ == '__main__':
    export_to_shopify_csv() 