import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

@app.route("/search-local", methods=["GET"])
def search_local():
    """
    Endpoint untuk mencari hasil lokal Google Maps menggunakan SerpApi.
    Menerima 'query' lengkap sebagai parameter URL, misal: "rumah sakit di Malang"
    """
    
    # Ambil parameter query lengkap
    query = request.args.get("query")
    
    if not query:
        return jsonify({"error": "Parameter 'query' diperlukan."}), 400

    if not SERPAPI_API_KEY:
        return jsonify({"error": "Kunci API SerpApi belum dikonfigurasi."}), 500

    print(f"Mencari '{query}'...")

    # Siapkan parameter SerpApi
    params = {
        "engine": "google_maps",
        "q": query,      # langsung query lengkap
        "hl": "id",
        "api_key": SERPAPI_API_KEY
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        local_results = data.get("local_results", [])
        if not local_results:
            return jsonify({
                "message": f"Tidak ditemukan hasil untuk '{query}'.",
                "full_response_metadata": data.get("search_metadata")
            }), 200

        simplified_results = []
        for result in local_results:
            simplified_results.append({
                "title": result.get("title"),
                "address": result.get("address"),
                "rating": result.get("rating"),
                "reviews": result.get("reviews"),
                "type": result.get("type"),
                "gps_coordinates": result.get("gps_coordinates"),
                "link": result.get("link")
            })

        return jsonify({
            "query_searched": query,
            "results_count": len(simplified_results),
            "local_results": simplified_results
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Permintaan ke SerpApi melebihi batas waktu."}), 504
    except requests.exceptions.RequestException as e:
        print(f"Kesalahan saat menghubungi SerpApi: {e}")
        return jsonify({"error": "Gagal menghubungi layanan eksternal.", "details": str(e)}), 500
    except Exception as e:
        print(f"Kesalahan tak terduga: {e}")
        return jsonify({"error": "Terjadi kesalahan internal server.", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
