from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import login_manager
from app import mysql
from datetime import datetime, timedelta
import MySQLdb
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from werkzeug.security import generate_password_hash


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("Anda tidak memiliki akses ke halaman ini.", "danger")
                return redirect(url_for('main.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            flash('Login berhasil!', 'success')
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.kasir_dashboard'))
        else:
            flash('Login gagal. Periksa username dan password.', 'danger')
    return render_template('login.html')

@main.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.kasir_dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM barang")
    total_barang = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM penjualan WHERE DATE(tanggal) = CURDATE()")
    total_transaksi_hari_ini = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total), 0) FROM penjualan WHERE DATE(tanggal) = CURDATE()")
    total_penjualan_hari_ini = cur.fetchone()[0]

    # Ambil data penjualan 7 hari terakhir
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        hari = datetime.now() - timedelta(days=i)
        label = hari.strftime('%a')
        chart_labels.append(label)

        cur.execute("SELECT COALESCE(SUM(total), 0) FROM penjualan WHERE DATE(tanggal) = %s", (hari.strftime('%Y-%m-%d'),))
        jumlah = cur.fetchone()[0]
        chart_data.append(jumlah)

    cur.close()

    return render_template('dashboard.html', 
                           total_barang=total_barang,
                           total_transaksi_hari_ini=total_transaksi_hari_ini,
                           total_penjualan_hari_ini=total_penjualan_hari_ini,
                           chart_labels=chart_labels,
                           chart_data=chart_data)

@main.route('/dashboard/kasir')
@login_required
def kasir_dashboard():
    if current_user.role != 'kasir':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('kasir_dashboard.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# Stok Barang Routes
@main.route('/barang')
@login_required
def list_barang():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM barang")
    data = cur.fetchall()
    cur.close()
    return render_template('barang_list.html', barang=data)

@main.route('/barang/tambah', methods=['GET', 'POST'])
@login_required
def tambah_barang():
    if request.method == 'POST':
        nama = request.form['nama']
        kategori = request.form['kategori']
        harga_beli = request.form['harga_beli']
        harga_jual = request.form['harga_jual']
        stok = request.form['stok']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO barang (nama, kategori, harga_beli, harga_jual, stok) VALUES (%s, %s, %s, %s, %s)",
                    (nama, kategori, harga_beli, harga_jual, stok))
        mysql.connection.commit()
        cur.close()
        flash('Barang berhasil ditambahkan!', 'success')
        return redirect(url_for('main.list_barang'))
    return render_template('barang_form.html')

# Edit Barang
@main.route('/barang/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_barang(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        nama = request.form['nama']
        kategori = request.form['kategori']
        harga_beli = request.form['harga_beli']
        harga_jual = request.form['harga_jual']
        stok = request.form['stok']
        cur.execute("""
            UPDATE barang SET nama=%s, kategori=%s, harga_beli=%s, harga_jual=%s, stok=%s WHERE id=%s
        """, (nama, kategori, harga_beli, harga_jual, stok, id))
        mysql.connection.commit()
        cur.close()
        flash('Barang berhasil diperbarui!', 'success')
        return redirect(url_for('main.list_barang'))
    cur.execute("SELECT * FROM barang WHERE id=%s", (id,))
    barang = cur.fetchone()
    cur.close()
    return render_template('barang_form.html', barang=barang)

# Hapus Barang
@main.route('/barang/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_barang(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM barang WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Barang berhasil dihapus.', 'success')
    return redirect(url_for('main.list_barang'))

# Transaksi
@main.route('/transaksi', methods=['GET', 'POST'])
@login_required
def transaksi():
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        barang_ids = request.form.getlist('barang_id[]')
        jumlahs = request.form.getlist('jumlah[]')
        total = 0
        detail_transaksi = []

        for barang_id, jumlah in zip(barang_ids, jumlahs):
            jumlah = int(jumlah)
            cur.execute("SELECT nama, harga_jual, stok FROM barang WHERE id = %s", (barang_id,))
            barang = cur.fetchone()

            if not barang:
                flash(f"Barang ID {barang_id} tidak ditemukan", "danger")
                return redirect(url_for('main.transaksi'))

            nama, harga_jual, stok = barang

            if jumlah > stok:
                flash(f"Stok barang '{nama}' tidak mencukupi", "danger")
                return redirect(url_for('main.transaksi'))

            subtotal = harga_jual * jumlah
            total += subtotal
            detail_transaksi.append((barang_id, jumlah, harga_jual, subtotal))

        cur.execute("INSERT INTO penjualan (tanggal, total) VALUES (NOW(), %s)", (total,))
        penjualan_id = cur.lastrowid

        for barang_id, jumlah, harga_jual, subtotal in detail_transaksi:
            cur.execute("""
                INSERT INTO penjualan_detail 
                (penjualan_id, barang_id, jumlah, harga_satuan, subtotal) 
                VALUES (%s, %s, %s, %s, %s)
            """, (penjualan_id, barang_id, jumlah, harga_jual, subtotal))
            cur.execute("UPDATE barang SET stok = stok - %s WHERE id = %s", (jumlah, barang_id))

        mysql.connection.commit()
        cur.close()
        flash("Transaksi berhasil disimpan!", "success")
        return redirect(url_for('main.transaksi'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, nama, harga_jual FROM barang WHERE stok > 0")
    barangs = cur.fetchall()
    cur.close()

    return render_template('transaksi.html', barangs=barangs)

#Laporan Penjualan
@main.route('/laporan_penjualan', methods=['GET', 'POST'])
@login_required
def laporan_penjualan():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    tanggal_awal = request.form.get('tanggal_awal')
    tanggal_akhir = request.form.get('tanggal_akhir')

    query = """
        SELECT p.id, p.tanggal, p.total, GROUP_CONCAT(CONCAT(b.nama, ' x', pd.jumlah) SEPARATOR ', ') AS detail
        FROM penjualan p
        JOIN penjualan_detail pd ON p.id = pd.penjualan_id
        JOIN barang b ON pd.barang_id = b.id
    """
    where_clause = ""
    params = []

    if tanggal_awal and tanggal_akhir:
        where_clause = " WHERE DATE(p.tanggal) BETWEEN %s AND %s"
        params = [tanggal_awal, tanggal_akhir]

    query += where_clause + " GROUP BY p.id ORDER BY p.tanggal DESC"

    cur.execute(query, params)
    penjualan = cur.fetchall()

    total_omzet = sum(item['total'] for item in penjualan)

    return render_template('laporan_penjualan.html',
                           penjualan=penjualan,
                           total_omzet=total_omzet,
                           tanggal_awal=tanggal_awal,
                           tanggal_akhir=tanggal_akhir)

#Laporan Excel
import csv
from flask import Response

@main.route('/export_penjualan_excel')
@login_required
def export_penjualan_excel():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki akses.', 'danger')
        return redirect(url_for('main.index'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.tanggal, b.nama, pd.jumlah, pd.harga_satuan, pd.subtotal
        FROM penjualan p
        JOIN penjualan_detail pd ON p.id = pd.penjualan_id
        JOIN barang b ON pd.barang_id = b.id
        ORDER BY p.tanggal DESC
    """)
    rows = cur.fetchall()
    cur.close()

    output = []
    header = ['Tanggal', 'Barang', 'Jumlah', 'Harga Satuan', 'Subtotal']
    output.append(header)

    for row in rows:
        output.append([
            row[0].strftime('%Y-%m-%d %H:%M:%S'),
            row[1],
            row[2],
            row[3],
            row[4]
        ])

    si = "\n".join([",".join(map(str, row)) for row in output])
    return Response(si, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=laporan_penjualan.csv"})

# Role
@main.route('/kelola_user')
@login_required
def kelola_user():
    if current_user.role != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))

    return render_template('kelola_user.html')

#Profile
@main.route('/profil')
@login_required
def profil():
    return render_template('profil.html', user=current_user)


# Buat akun
@main.route('/register_kasir', methods=['GET', 'POST'])
@login_required
def register_kasir():
    if current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                    (username, hashed_pw, 'kasir'))
        mysql.connection.commit()
        cur.close()

        flash('Akun kasir berhasil dibuat!', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('register_kasir.html')
