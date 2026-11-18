import re

def extract_barcode(message):
    digits = re.findall(r"(?<!\d)\d{8,14}(?!\d)", message)
    return digits[0] if digits else None

def _format(value, unit=""):
    if value is None:
        return "belum tersedia"
    return f"{value:g}{unit}"

def product_reply(product):
    if not product:
        return None
    lines = [
        f"**{product['product_name']}**",
        f"Merek: {product['brands'] or 'Tidak tercantum'}",
        f"Ukuran: {product['quantity'] or 'Tidak tercantum'}",
        "",
        "Informasi per 100 gram/ml (jika tercantum pada sumber):",
        f"- Energi: {_format(product['energy_kcal_100g'], ' kkal')}",
        f"- Gula: {_format(product['sugars_100g'], ' g')}",
        f"- Protein: {_format(product['proteins_100g'], ' g')}",
        f"- Lemak: {_format(product['fat_100g'], ' g')}",
        f"- Karbohidrat: {_format(product['carbohydrates_100g'], ' g')}",
        f"- Garam: {_format(product['salt_100g'], ' g')}",
    ]
    if product["ingredients_text"]:
        lines += ["", f"Bahan: {product['ingredients_text'][:700]}"]
    lines += ["", f"Sumber data: {product['source_url']}",
              "Catatan: data berasal dari kontribusi komunitas dan bisa tidak lengkap. Periksa label kemasan asli."]
    return "\n".join(lines)

def generate_reply(message, product, education_search):
    if product:
        return product_reply(product), {"type": "product", "barcode": product["barcode"]}

    text = message.lower()
    if any(word in text for word in ["halo", "hai", "hello", "selamat pagi", "selamat siang"]):
        return ("Halo! Aku LabelGizi Bot. Aku bisa membantu mencari informasi kandungan produk "
                "berdasarkan barcode dan mencari materi edukasi gizi. Apa yang ingin kamu ketahui?"), {"type": "greeting"}

    if any(word in text for word in ["barcode", "kandungan", "nutrisi", "kalori", "gula", "protein", "lemak", "produk"]):
        return ("Untuk memeriksa produk, kirimkan **angka barcode** yang tertera di kemasan (8–14 digit). "
                "Aku akan mencoba mengambil informasi produk dari Open Food Facts. "
                "Jika produk belum terdaftar, data mungkin tidak ditemukan."), {"type": "barcode_help"}

    terms = ["gizi", "piringku", "seimbang", "sayur", "buah", "makan", "nutrisi", "label"]
    if any(word in text for word in terms):
        results = education_search(message, limit=3)
        if results:
            parts = ["Aku menemukan materi edukasi berikut dari sumber yang tersimpan:"]
            for item in results:
                snippet = (item["content"] or "").replace("\n", " ")
                parts.append(f"\n**{item['title']}**\n{snippet[:650]}...\nSumber: {item['url']}")
            return "\n".join(parts), {"type": "education", "count": len(results)}
        return ("Aku belum menemukan materi yang cocok di database lokal. Kamu tetap bisa mencoba pertanyaan "
                "tentang cara membaca label gizi, Isi Piringku, atau gula-garam-lemak. "
                "Materi dari situs Kemenkes bisa belum terambil jika server sumber sedang tidak tersedia."), {"type": "education_empty"}

    return ("Aku belum memahami pertanyaan itu. Coba kirim barcode produk, atau tanyakan tentang "
            "gizi seimbang, Isi Piringku, gula, protein, dan label nutrisi. "
            "Jawabanku terbatas pada data yang tersedia di sumber proyek."), {"type": "fallback"}
