from loguru import logger
import pandas as pd
import os
from .database import Database

def export_to_shopify_csv(output_dir='shopify_exports'):
    """
    Veritabanındaki ürünleri tek bir Shopify CSV dosyasına export eder.
    """
    try:
        # Veritabanına bağlan
        db = Database()
        db.connect()
        
        # Ürünleri getir
        products_df = db.get_all_products()
        total_products = len(products_df)
        logger.info(f"Toplam {total_products} ürün export edilecek")
        
        # Shopify CSV formatına dönüştür
        shopify_data = []
        for _, product in products_df.iterrows():
            # Resim URL'sini kontrol et
            if not product['image_url'] or pd.isna(product['image_url']):
                continue
                
            # Stok miktarını al
            stock_qty = product['availability']
            if not stock_qty or pd.isna(stock_qty):
                stock_qty = '0'
                
            shopify_product = {
                'Handle': product['sku'].lower().replace(' ', '-'),  # URL-friendly handle
                'Title': product['title'] or f"INSIZE {product['sku']}",
                'Body (HTML)': product['description'] or '',
                'Vendor': 'INSIZE',
                'Type': 'Tools & Equipment',  # Shopify standart kategori
                'Tags': f"insize, measuring tools, {product['category'] or ''}, {product['subcategory'] or ''}",
                'Published': 'TRUE' if stock_qty != '0' else 'FALSE',
                'Option1 Name': 'Title',
                'Option1 Value': 'Default Title',
                'Variant SKU': product['sku'],
                'Variant Inventory Tracker': 'shopify',
                'Variant Inventory Qty': stock_qty,  # INSIZE'dan gelen gerçek stok miktarı
                'Variant Inventory Policy': 'deny',
                'Variant Fulfillment Service': 'manual',
                'Variant Price': str(product['price'] or 0),
                'Variant Compare At Price': str(product['original_price']) if product['original_price'] else '',
                'Variant Requires Shipping': 'TRUE',
                'Variant Taxable': 'TRUE',
                'Image Src': product['image_url'],
                'Image Position': '1',
                'Status': 'active' if stock_qty != '0' else 'draft',
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
        
        # Klasörü oluştur
        os.makedirs(output_dir, exist_ok=True)
        
        # Tüm ürünleri tek bir CSV dosyasına yaz
        output_file = os.path.join(output_dir, 'shopify_products.csv')
        shopify_df = pd.DataFrame(shopify_data)
        shopify_df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Toplam {len(shopify_data)} ürün {output_file} dosyasına kaydedildi")
        
        logger.success(f"Toplam {len(shopify_data)} ürün başarıyla export edildi")
        
    except Exception as e:
        logger.error(f"CSV export hatası: {str(e)}")
        raise
    finally:
        if db:
            db.close()

if __name__ == '__main__':
    export_to_shopify_csv() 