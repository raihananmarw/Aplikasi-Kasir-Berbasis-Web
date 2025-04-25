# Aplikasi Kasir Berbasis Web

Aplikasi kasir berbasis web menggunakan Flask dan MySQL. Aplikasi ini mendukung dua peran pengguna (Admin dan Kasir), dengan fitur-fitur untuk manajemen stok barang, transaksi penjualan, laporan penjualan, dan pengelolaan akun kasir.

## 🚀 Fitur Utama

### 1. Login dan Role-based Access
- Autentikasi pengguna menggunakan Flask-Login
- Role "admin" dan "kasir"
- Navbar dan akses menu dinamis berdasarkan role

### 2. Dashboard
- Admin: Total barang, total transaksi hari ini, total pendapatan hari ini
- Kasir: Ringkasan transaksi dan akses cepat

### 3. Manajemen Barang (Admin)
- Tambah, Edit, Hapus Barang
- Tabel stok barang berisi: Nama, Kategori, Harga Beli, Harga Jual, dan Stok

### 4. Transaksi Penjualan
- Tambahkan barang ke keranjang
- Hitung total transaksi
- Kurangi stok otomatis saat transaksi selesai

### 5. Laporan Penjualan (Admin)
- Histori penjualan
- Filter berdasarkan tanggal
- Menampilkan total transaksi dan barang terjual

### 6. Manajemen Akun Kasir (Admin)
- Registrasi akun kasir
- Edit / Hapus akun kasir

### 7. Profil Pengguna
- Lihat informasi akun login aktif

## 🛠 Teknologi yang Digunakan
- Python 3.10+
- Flask
- MySQL
- flask-mysqldb
- flask-login
- Bootstrap 5.3
- Bootstrap Icons
- Chart.js

## 📁 Struktur Direktori

```
project/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── db.py
│   ├── templates/
│   │   ├── layout.html
│   │   ├── navbar.html
│   │   ├── login.html
│   │   ├── dashboard_admin.html
│   │   ├── dashboard_kasir.html
│   │   ├── daftar_barang.html
│   │   ├── transaksi.html
│   │   └── ...
│   └── static/
│       └── css/, js/, images/
├── config.py
├── run.py
└── requirements.txt
```

## 🧩 Struktur Database (Sederhana)

- `users`: id, username, password, role
- `barang`: id, nama, kategori, harga_beli, harga_jual, stok
- `penjualan`: id, tanggal, total, user_id
- `penjualan_detail`: id, penjualan_id, barang_id, jumlah, harga

## 📌 Cara Menjalankan Aplikasi

1. Clone repositori ini
2. Install dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```
3. Atur konfigurasi database di `config.py`
4. Jalankan server:
   ```bash
   python run.py
   ```

## 📄 Lisensi

Aplikasi ini bersifat open source dan bebas digunakan serta dimodifikasi untuk keperluan pembelajaran dan pengembangan bisnis.
