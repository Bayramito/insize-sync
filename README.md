# INSIZE Shopify Sync

Bu proje, INSIZE ürün kataloğunu Excel dosyasından alıp Shopify'a import edilebilir CSV formatına dönüştüren bir Python uygulamasıdır.

## Özellikler

- INSIZE Excel dosyasından ürün verilerini okuma
- Stok durumu kontrolü ve filtreleme
- Shopify CSV formatına dönüştürme
- Tek bir CSV dosyası oluşturma
- Resim URL'lerini kontrol etme
- Özel alanlar (metafields) desteği

## Gereksinimler

- Python 3.8 veya üzeri
- PostgreSQL 12 veya üzeri
- pip (Python paket yöneticisi)

## Kurulum

### macOS

1. Python kurulumu (eğer yüklü değilse):

   ```bash
   # Homebrew ile Python kurulumu
   brew install python

   # veya Python web sitesinden indirip kurabilirsiniz:
   # https://www.python.org/downloads/macos/
   ```

2. PostgreSQL kurulumu:

   ```bash
   brew install postgresql@14
   brew services start postgresql@14
   ```

3. Proje kurulumu:

   ```bash
   # Projeyi klonlayın
   git clone <proje-url>
   cd insize-sync

   # Virtual environment oluşturun
   python3 -m venv venv
   source venv/bin/activate

   # Gereksinimleri yükleyin
   pip install -r requirements.txt
   ```

### Windows

1. Python kurulumu:

   - https://www.python.org/downloads/windows/ adresinden Python 3.8+ indirin
   - Kurulum sırasında "Add Python to PATH" seçeneğini işaretleyin

2. PostgreSQL kurulumu:

   - https://www.postgresql.org/download/windows/ adresinden PostgreSQL indirin
   - Kurulum sırasında şifrenizi not alın

3. Proje kurulumu:

   ```cmd
   # Projeyi klonlayın
   git clone [text](https://github.com/Bayramito/insize-sync.git)
   cd insize-sync

   # Virtual environment oluşturun
   python -m venv venv
   .\venv\Scripts\activate

   # Gereksinimleri yükleyin
   pip install -r requirements.txt
   ```

### Linux (Ubuntu/Debian)

1. Python ve PostgreSQL kurulumu:

   ```bash
   # Gerekli paketleri yükleyin
   sudo apt update
   sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib

   # PostgreSQL servisini başlatın
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

2. Proje kurulumu:

   ```bash
   # Projeyi klonlayın
   git clone <proje-url>
   cd insize-sync

   # Virtual environment oluşturun
   python3 -m venv venv
   source venv/bin/activate

   # Gereksinimleri yükleyin
   pip install -r requirements.txt
   ```

## Veritabanı Yapılandırması

1. `.env` dosyasını oluşturun:

   ```env
   # INSIZE Credentials
   INSIZE_USERNAME=your_username
   INSIZE_PASSWORD=your_password
   INSIZE_EXCEL_URL=https://eshop.insize-eu.com/ERP/INSIZE_EUROPE.xlsx

   # PostgreSQL configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=insize_sync
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

2. Veritabanını oluşturun:

   ```bash
   # macOS / Linux
   createdb insize_sync

   # Windows (PostgreSQL kurulum dizininde)
   createdb.exe -U postgres insize_sync
   ```

## Kullanım

1. Virtual environment'ı aktifleştirin:

   ```bash
   # macOS / Linux
   source venv/bin/activate

   # Windows
   .\venv\Scripts\activate
   ```

2. Uygulamayı çalıştırın:

   ```bash
   # Tüm işletim sistemlerinde aynı
   python -m src.sync_all
   ```

3. CSV dosyası `shopify_exports` klasöründe oluşturulacaktır:
   - `shopify_products.csv`: Tüm ürünlerin bulunduğu dosya

## Shopify'a Import

1. Shopify admin panelinde Products > Import'a gidin
2. `shopify_exports/shopify_products.csv` dosyasını yükleyin

## Proje Yapısı

```
insize-sync/
├── src/
│   ├── __init__.py
│   ├── config.py        # Yapılandırma ayarları
│   ├── database.py      # Veritabanı işlemleri
│   ├── downloader.py    # Excel indirme
│   ├── parser.py        # Excel parse etme
│   ├── csv_exporter.py  # CSV export
│   └── sync_all.py      # Ana script
├── tests/               # Test dosyaları
├── shopify_exports/     # Oluşturulan CSV'ler
├── requirements.txt     # Python bağımlılıkları
├── .env                 # Ortam değişkenleri
└── README.md
```

## Hata Ayıklama

### macOS

1. PostgreSQL bağlantı hatası:

   ```bash
   brew services restart postgresql@14
   ```

2. Python path hatası:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/proje/dizini"
   ```

### Windows

1. PostgreSQL bağlantı hatası:

   - Services uygulamasında PostgreSQL servisini yeniden başlatın
   - Veya komut isteminde:
     ```cmd
     net stop postgresql
     net start postgresql
     ```

2. Python path hatası:
   ```cmd
   set PYTHONPATH=%PYTHONPATH%;C:\proje\dizini
   ```

### Linux

1. PostgreSQL bağlantı hatası:

   ```bash
   sudo systemctl restart postgresql
   ```

2. Python path hatası:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/proje/dizini"
   ```

## Güvenlik

- `.env` dosyasını asla git repository'sine eklemeyin
- PostgreSQL şifrenizi güvenli bir yerde saklayın
- Veritabanı yedeklerini düzenli olarak alın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.
