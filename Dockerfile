# Menggunakan base image Python resmi
FROM python:3.11-slim

# Menetapkan direktori kerja di dalam container
WORKDIR /app

# Menyalin file requirements.txt dan menginstal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin kode aplikasi ke dalam container
COPY . .

# Secara default, Flask akan berjalan pada port 5000, 
# tetapi aplikasi di atas menggunakan variabel lingkungan PORT.
EXPOSE 5000

# Menentukan perintah untuk menjalankan aplikasi
# Menggunakan Gunicorn adalah praktik yang lebih baik untuk production daripada flask run
# Namun, untuk kesederhanaan, kita tetap menggunakan skrip Python langsung:
# CMD ["python", "app.py"]

# Alternatif: Menggunakan Gunicorn (disarankan untuk produksi)
# Anda perlu menambahkan 'gunicorn' ke requirements.txt jika menggunakan ini:
# CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
CMD ["python", "app.py"]