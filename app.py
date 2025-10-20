import os
import requests
from flask import Flask, request, jsonify

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Mengambil kunci API dari environment variables (Penting untuk keamanan)
# Variabel ini harus diatur di konfigurasi Railway Anda.
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

@app.route("/search-local", methods=["GET"])
def search_local():
    """
    Endpoint untuk mencari hasil lokal Google Maps menggunakan SerpApi.
    Menerima 'city' (nama kota dari Maps API) dan 'query' (pencarian, misal: "rumah sakit") 
    sebagai parameter URL.
    """
    
    # 1. Ambil parameter dari request
    city = request.args.get("city")
    query = request.args.get("query")
    
    # Validasi input
    if not city or not query:
        return jsonify({
            "error": "Parameter 'city' (nama kota) dan 'query' (kata kunci pencarian) diperlukan."
        }), 400

    if not SERPAPI_API_KEY:
        return jsonify({
            "error": "Kunci API SerpApi (SERPAPI_API_KEY) tidak dikonfigurasi di server."
        }), 500

    print(f"Mencari '{query}' di kota '{city}'...")

    # 2. Siapkan parameter untuk SerpApi
    # Parameter 'location' akan menggunakan nama kota (misal: "Jakarta") untuk memfokuskan pencarian.
    params = {
        "engine": "google_maps",
        "q": query,
        "location": city, 
        "hl": "id", # Menggunakan Bahasa Indonesia untuk hasil (opsional, bisa 'en')
        "api_key": SERPAPI_API_KEY
    }

    # 3. Lakukan permintaan ke SerpApi
    try:
        # Gunakan timeout agar permintaan tidak menggantung selamanya
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status() # Akan memicu exception untuk bad status codes (4xx atau 5xx)
        data = response.json()
        
        # 4. Filter data dan kembalikan hanya hasil lokal (local_results)
        local_results = data.get("local_results", [])
        
        if not local_results:
             return jsonify({
                "message": f"Tidak ditemukan hasil lokal untuk '{query}' di '{city}'.",
                "full_response_metadata": data.get("search_metadata")
            }), 200

        # Hanya ambil informasi penting dari setiap hasil untuk payload yang ringkas
        simplified_results = []
        for result in local_results:
            simplified_results.append({
                "title": result.get("title"),
                "address": result.get("address"),
                "rating": result.get("rating"),
                "reviews": result.get("reviews"),
                "type": result.get("type"),
                "gps_coordinates": result.get("gps_coordinates"),
                # Sertakan link Google Maps untuk navigasi
                "link": result.get("link") 
            })

        return jsonify({
            "city_searched": city,
            "query_searched": query,
            "results_count": len(simplified_results),
            "local_results": simplified_results
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Permintaan ke SerpApi melebihi batas waktu (timeout)."
        }), 504
    except requests.exceptions.RequestException as e:
        # Menangani kesalahan koneksi atau kesalahan HTTP
        print(f"Kesalahan saat menghubungi SerpApi: {e}")
        return jsonify({
            "error": "Gagal menghubungi layanan pencarian eksternal.",
            "details": str(e)
        }), 500
    except Exception as e:
        # Menangani kesalahan tak terduga lainnya
        print(f"Kesalahan tak terduga: {e}")
        return jsonify({
            "error": "Terjadi kesalahan internal pada server.",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    # Gunakan host 0.0.0.0 dan port yang disediakan oleh environment (Railway)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
