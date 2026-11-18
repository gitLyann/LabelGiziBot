from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from database import init_db, save_product, search_education, save_chat_message, get_recent_messages
from services.openfoodfacts import get_product
from chatbot.engine import generate_reply, extract_barcode

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-this")
init_db()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "app": "LabelGizi Bot"})

@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Tulis pertanyaan terlebih dahulu."}), 400

    save_chat_message("user", message)
    barcode = extract_barcode(message)
    product = None
    if barcode:
        try:
            product = get_product(barcode)
            if product:
                save_product(product)
        except Exception as exc:
            app.logger.exception("Gagal mengambil produk dari Open Food Facts")
            reply = ("Maaf, layanan data produk sedang tidak dapat dihubungi. "
                     "Coba lagi beberapa saat atau periksa koneksi internet.")
            save_chat_message("assistant", reply)
            return jsonify({"reply": reply, "error": "upstream_api_error"}), 502

    reply, metadata = generate_reply(message, product, search_education)
    save_chat_message("assistant", reply)
    return jsonify({"reply": reply, "metadata": metadata})

@app.get("/api/product/<barcode>")
def product_detail(barcode):
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "Barcode harus berupa 8–14 digit angka."}), 400
    try:
        product = get_product(barcode)
        if not product:
            return jsonify({"error": "Produk tidak ditemukan di Open Food Facts."}), 404
        save_product(product)
        return jsonify({"product": product})
    except Exception:
        app.logger.exception("Product lookup failed")
        return jsonify({"error": "Tidak dapat menghubungi Open Food Facts."}), 502

@app.get("/api/education")
def education():
    q = (request.args.get("q") or "").strip()
    return jsonify({"items": search_education(q, limit=8)})

@app.get("/api/history")
def history():
    return jsonify({"messages": get_recent_messages(limit=30)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
