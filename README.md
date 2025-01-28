# INSIZE Shopify Sync

Bu proje, INSIZE ürün kataloğunu Shopify'a senkronize etmek için kullanılan bir Python uygulamasıdır.

## Özellikler

- Veritabanındaki ürünleri Shopify CSV formatına dönüştürme
- Toplu ürün yükleme için batch işleme (1000 ürün/dosya)
- Resim URL'si kontrolü
- Shopify standart kategori yapısına uygun export
- Özel alanlar (metafields) desteği

## Kurulum

1. Python 3.8+ yüklü olmalıdır
2. Virtual environment oluşturun:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # veya
   .\venv\Scripts\activate  # Windows
   ```
3. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Kullanım

### CSV Export

Ürünleri Shopify CSV formatında export etmek için:

```bash
python -m tests.test_csv_export
```

Bu komut, `shopify_exports` klasöründe her biri 1000 ürün içeren CSV dosyaları oluşturacaktır.

### Shopify'a Yükleme

1. Shopify admin panelinde Products > Import'a gidin
2. `shopify_exports` klasöründeki CSV dosyalarını sırayla yükleyin

## Proje Yapısı

```
insize-sync/
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── csv_exporter.py
│   └── shopify_sync.py
├── tests/
│   ├── __init__.py
│   ├── test_csv_export.py
│   └── test_shopify_sync.py
├── requirements.txt
└── README.md
```
