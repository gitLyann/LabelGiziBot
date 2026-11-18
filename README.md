# LabelGizi Bot

Starter project chatbot edukasi informasi gizi berbasis Flask, SQLite, Open Food Facts REST API, dan scraping artikel publik Ayo Sehat Kemenkes.

## Fitur awal
- Chatbot rule-based sederhana.
- Pencarian detail produk berdasarkan barcode melalui Open Food Facts API v3.
- Penyimpanan cache produk ke SQLite.
- Scraping terbatas artikel edukasi Kemenkes menggunakan Requests + BeautifulSoup.
- Materi ringkas edukasi lokal sebagai fallback jika scraping gagal.
- Pencarian materi edukasi yang sudah tersimpan di database berdasarkan kata kunci.
- Riwayat pesan dasar.
- Antarmuka responsif.

## Persyaratan
- Python 3.10 atau lebih baru
- Koneksi internet untuk API dan scraping

## Menjalankan di Windows (PowerShell)

1. Ekstrak ZIP.
2. Buka folder `LabelGiziBot` di VS Code.
3. Buka Terminal > New Terminal.
4. Buat virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Jika PowerShell memblokir aktivasi, gunakan Command Prompt atau jalankan:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

5. Pasang dependensi:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Salin `.env.example` menjadi `.env` dan ubah `SECRET_KEY`. Untuk pengujian lokal, aplikasi tetap dapat berjalan dengan nilai pengembangan bawaan, tetapi jangan gunakan nilai tersebut untuk deployment.

7. Jalankan scraper satu kali untuk mencoba mengambil artikel edukasi dari Kemenkes:

   ```powershell
   python scraper.py
   ```

   Scraper hanya mengunjungi dua URL yang ditentukan pada `scraper.py`, dengan satu kali percobaan ulang jika terjadi gangguan sementara. Jika server Kemenkes mengembalikan HTTP 503, itu berarti server sumber sedang tidak tersedia atau menolak permintaan. Ini tidak menghentikan website. Database juga otomatis diisi tiga materi ringkas lokal (label gizi, Isi Piringku, serta gula-garam-lemak) sebagai fallback. Materi lokal tersebut adalah ringkasan edukatif, bukan hasil scraping otomatis, dan menyertakan tautan sumber untuk dibaca lebih lanjut.

8. Jalankan website:

   ```powershell
   python app.py
   ```

9. Buka `http://127.0.0.1:5000`.

## Menguji pencarian produk
Cari barcode pada kemasan produk, lalu kirim angka barcode (8–14 digit) melalui chat. Data hanya muncul jika produk tersedia di Open Food Facts. Data nutrisi yang kosong ditampilkan sebagai "belum tersedia".

Contoh barcode demo yang tercantum dalam dokumentasi Open Food Facts:
`3274080005003`

Tidak semua barcode produk Indonesia pasti tersedia. Ketersediaan dan kelengkapan data bergantung pada kontribusi komunitas.

## Struktur folder

```text
LabelGiziBot/
├── app.py
├── database.py
├── scraper.py
├── chatbot/
│   └── engine.py
├── services/
│   └── openfoodfacts.py
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
├── instance/              # database dibuat otomatis
├── requirements.txt
├── .env.example
└── README.md
```

## Endpoint internal
- `GET /` — halaman chatbot
- `GET /api/health` — pemeriksaan server
- `POST /api/chat` — kirim pesan chatbot
- `GET /api/product/<barcode>` — detail produk
- `GET /api/education?q=...` — cari materi edukasi tersimpan
- `GET /api/history` — riwayat pesan lokal

Contoh request chat:

```json
{
  "message": "Bagaimana cara membaca label gizi?"
}
```

## Sumber data dan atribusi
1. Open Food Facts: https://openfoodfacts.org/ — API dokumentasi: https://openfoodfacts.github.io/documentation/
2. Ayo Sehat Kementerian Kesehatan RI: https://ayosehat.kemkes.go.id/
3. Artikel awal yang dijadikan target scraper:
   https://ayosehat.kemkes.go.id/isi-piringku-kebutuhan-gizi-harian-seimbang
   https://ayosehat.kemkes.go.id/1000-hari-pertama-kehidupan/balita

Open Food Facts meminta custom User-Agent dan membatasi permintaan baca produk hingga 15 request/menit/IP serta pencarian hingga 10 request/menit/IP. Hormati batas dan ketentuan lisensi ODbL/atribusi. Jangan melakukan scraping massal. Periksa robots.txt dan ketentuan situs sebelum menambah URL scraper.

## Batasan penting
- Ini starter project untuk pembelajaran, belum aplikasi produksi.
- Bot tidak mendiagnosis penyakit, tidak memberikan terapi, dan tidak menggantikan dokter/ahli gizi.
- Nilai nutrisi per 100g/ml ditampilkan hanya jika tersedia di sumber. Jangan menganggap data kosong berarti nilai nol.
- Fitur "bersihkan" saat ini hanya membersihkan tampilan browser; riwayat di database tetap tersimpan.
- Riwayat saat ini bersifat lokal bersama, belum dipisahkan per akun/sesi pengguna.
- Scraper menyimpan teks artikel yang diekstrak; selalu tampilkan URL sumber dan jangan menyalin ulang konten secara berlebihan.

## Pengembangan berikutnya
1. Tambahkan pemisahan sesi pengguna.
2. Buat halaman riwayat dan dashboard admin.
3. Tambahkan pencarian produk dengan metode yang sesuai API resmi (v3 belum menyediakan full-text search).
4. Tambahkan pengujian otomatis.
5. Tambahkan validasi dan pengamanan sebelum deployment.
