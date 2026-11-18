import os
import requests

BASE_URL = "https://world.openfoodfacts.org/api/v3/product"
USER_AGENT = os.getenv("OPENFOODFACTS_USER_AGENT", "LabelGiziBot/0.1 (student-project; contact: replace-with-your-email@example.com)")

def _number(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

def get_product(barcode):
    """Ambil satu produk berdasarkan barcode dari Open Food Facts API v3."""
    url = f"{BASE_URL}/{barcode}.json"
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success" or not data.get("product"):
        return None

    product = data["product"]
    nutriments = product.get("nutriments") or {}
    name = product.get("product_name_id") or product.get("product_name") or "Nama produk tidak tersedia"

    return {
        "barcode": str(barcode),
        "product_name": name,
        "brands": product.get("brands") or "",
        "quantity": product.get("quantity") or "",
        "ingredients_text": product.get("ingredients_text_id") or product.get("ingredients_text") or "",
        "energy_kcal_100g": _number(nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal_value")),
        "sugars_100g": _number(nutriments.get("sugars_100g")),
        "fat_100g": _number(nutriments.get("fat_100g")),
        "saturated_fat_100g": _number(nutriments.get("saturated-fat_100g")),
        "proteins_100g": _number(nutriments.get("proteins_100g")),
        "carbohydrates_100g": _number(nutriments.get("carbohydrates_100g")),
        "salt_100g": _number(nutriments.get("salt_100g")),
        "image_url": product.get("image_front_url") or product.get("image_url") or "",
        "source_url": f"https://world.openfoodfacts.org/product/{barcode}"
    }
