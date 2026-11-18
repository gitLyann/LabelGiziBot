"""
Scraper edukasi terbatas untuk artikel publik Ayo Sehat Kemenkes.
Jalankan manual: python scraper.py
Jangan gunakan untuk crawling massal. Periksa ketentuan situs sebelum scraping.
"""
import requests
import time
from bs4 import BeautifulSoup
from database import init_db, save_education_article

SEED_URLS = [
    "https://ayosehat.kemkes.go.id/isi-piringku-kebutuhan-gizi-harian-seimbang",
    "https://ayosehat.kemkes.go.id/1000-hari-pertama-kehidupan/balita",
]
HEADERS = {
    "User-Agent": "LabelGiziBot/0.1 (educational student project; respectful low-volume access)"
}

def scrape_article(url):
    # Retry terbatas untuk gangguan sementara. Tidak melakukan crawling berulang.
    response = None
    for attempt in range(2):
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 1:
                raise
            time.sleep(3)
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    title = ""
    if soup.find("h1"):
        title = soup.find("h1").get_text(" ", strip=True)
    elif soup.title:
        title = soup.title.get_text(" ", strip=True)

    main = soup.find("article") or soup.find("main") or soup.body or soup
    paragraphs = [el.get_text(" ", strip=True) for el in main.find_all(["p", "li", "h2", "h3"])]
    content = "\n".join(text for text in paragraphs if len(text) > 35)
    content = content[:20000]

    if not title or not content:
        raise ValueError("Konten artikel tidak berhasil diekstrak; struktur halaman mungkin berubah.")

    save_education_article(url, title, content)
    return title, len(content)

def main():
    init_db()  # Materi ringkas lokal otomatis tersedia meskipun situs sumber gagal.
    success = 0
    for url in SEED_URLS:
        try:
            title, chars = scrape_article(url)
            success += 1
            print(f"[OK] {title} — {chars} karakter")
        except Exception as exc:
            print(f"[GAGAL] {url}: {exc}")
    print(f"\nSelesai: {success}/{len(SEED_URLS)} artikel berhasil di-scrape.")
    print("Materi ringkas lokal tetap tersedia di database; website tetap dapat digunakan.")

if __name__ == "__main__":
    main()
