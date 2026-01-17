import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import base64
import os


# Pastikan file "LOGO INVOICE.png" sudah ada di folder yang sama di GitHub
st.set_page_config(
    page_title="3G LOGISTICS - System", 
    page_icon="3G.png", # Ini akan mengganti icon tab browser
    layout="wide"
)

# --- PASTE URL WEB APP DARI GOOGLE APPS SCRIPT DI SINI ---
URL_SCRIPT_GOOGLE = "ISI_DENGAN_URL_DARI_APPS_SCRIPFT_ANDA"

# --- FUNGSI MUAT DATA (READ ONLY) ---
# Menggunakan link CSV untuk tampilan database yang ringan
URL_SHEET_CSV = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/export?format=csv"

def muat_data():
    try:
        return pd.read_csv(URL_SHEET_CSV).fillna('')
    except:
        return pd.DataFrame(columns=["Tanggal", "Resi", "Pengirim", "Penerima", "Produk", "Origin", "Destination", "Kolli", "Berat", "Harga", "Total"])

# --- FUNGSI TERBILANG ---
def terbilang(n):
    n = int(n)
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[n]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return "Angka terlalu besar"

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Menampilkan Logo dan Judul berdampingan
col_logo, col_text = st.columns([1, 5])
with col_logo:
    st.image("3G.png", width=150) # Sesuaikan ukuran logo di sini
with col_text:
    st.title("PT. GAMA GEMAH GEMILANG")

if 'df' not in st.session_state:
    st.session_state.df = muat_data()

tab1, tab2, tab3 = st.tabs(["➕ Input Pengiriman", "📋 Database (Google Sheets)", "📄 Cetak Invoice"])

with tab1:
    with st.form("form_input", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No. Resi")
            pengirim = st.text_input("Nama Customer (Pengirim)")
            produk = st.text_input("Deskripsi Produk")
            origin = st.text_input("Origin")
        with c2:
            penerima = st.text_input("Nama Penerima")
            destination = st.text_input("Destination")
            kolli = st.number_input("KOLLI", min_value=1, value=1)
            berat = st.number_input("Weight (Kg)", min_value=1, value=1)
            harga_satuan = st.number_input("Harga Satuan (Rp)", min_value=0, value=0)
        
        if st.form_submit_button("Simpan Data ke Cloud"):
            total = berat * harga_satuan
            data_json = {
                "Tanggal": datetime.now().strftime("%d-%b-%y"),
                "Resi": resi, "Pengirim": pengirim, "Penerima": penerima,
                "Produk": produk, "Origin": origin, "Destination": destination,
                "Kolli": kolli, "Berat": berat, "Harga": harga_satuan, "Total": total
            }
            
            try:
                # Mengirim data ke Google Sheets melalui Apps Script
                response = requests.post("https://script.google.com/macros/s/AKfycbz-bMYzT2f_WYvuM-2-Mo5D6KhPrwRwQMN9JhIC1dotbHtfGE9RNHMrSYNNxnvbitPr/exec", json=data_json)
                if response.status_code == 200:
                    st.success("✅ DATA BERHASIL DISIMPAN KE GOOGLE SHEETS!")
                    st.session_state.df = muat_data() # Refresh data
                    st.rerun()
                else:
                    st.error(f"Gagal Simpan. Status: {response.status_code}")
            except Exception as e:
                st.error(f"Koneksi Error: {e}")

with tab2:
    st.subheader("📋 Data Real-time dari Google Sheets")
    if st.button("Refresh Data"):
        st.session_state.df = muat_data()
        st.rerun()
    st.dataframe(st.session_state.df, use_container_width=True)

with tab3:
    st.subheader("📄 Preview & Cetak Invoice")
    
    # Refresh data terbaru
    df_cetak = muat_data()
    
    if not df_cetak.empty:
        # Menampilkan daftar resi terbaru di atas
        list_resi = df_cetak["Resi"].unique().tolist()
        resi_sel = st.selectbox("Pilih Nomor Resi untuk Dicetak", list_resi[::-1])
        
        if resi_sel:
            # Ambil data satu baris
            d = df_cetak[df_cetak["Resi"] == resi_sel].iloc[0]
            
            # --- FUNGSI DETEKSI KOLOM OTOMATIS ---
            # Ini mencegah KeyError jika nama kolom di Sheets berubah-ubah
            def get_val(possible_names, default=0):
                for name in possible_names:
                    if name in d: return d[name]
                return default

            v_harga = get_val(['Harga', 'Harga Satuan', 'PRICE'])
            v_berat = get_val(['Berat', 'Berat (kg)', 'WEIGHT'])
            v_total = get_val(['Total', 'Total Biaya', 'TOTAL'])
            v_kolli = get_val(['Kolli', 'KOLLI', 'Qty'])

            # Load Gambar
            logo = get_image_base64("LOGO INVOICE.png")
            ttd = get_image_base64("TANDA TANGAN.png")
            stempel = get_image_base64("STEMPEL DAN NAMA.png")
            
            # Pastikan angka valid
            try:
                total_float = float(v_total)
                harga_float = float(v_harga)
            except:
                total_float = 0
                harga_float = 0

           # Tampilan Invoice HTML yang sudah dirapikan
st.markdown(f"""
<div style="border: 2px solid #1a3d8d; padding: 40px; background-color: white; color: black; font-family: 'Arial', sans-serif; border-radius: 10px;">
    <table style="width:100%; border:none; margin-bottom: 10px;">
        <tr>
            <td style="width:25%; border:none; vertical-align: middle;">
                <img src="data:image/png;base64,{logo}" style="width:160px;">
            </td>
            <td style="border:none; text-align:left; vertical-align: middle; padding-left: 20px;">
                <h2 style="margin:0; color: #1a3d8d; font-size: 26px;">PT. GAMA GEMAH GEMILANG</h2>
                <p style="font-size:12px; margin:2px 0; color: #555;">
                    Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan,<br>
                    Menganti, Gresik, Jawa Timur. <br>
                    <strong>Telp:</strong> 031-79973432 | <strong>Email:</strong> finance@3glogistics.com
                </p>
            </td>
            <td style="width:25%; border:none; text-align:right; vertical-align: top;">
                <h1 style="margin:0; color: #d62828; font-size: 28px; letter-spacing: 2px;">INVOICE</h1>
                <p style="margin:0; font-weight: bold;">#{d['Resi']}</p>
            </td>
        </tr>
    </table>

    <div style="border-top: 3px solid #1a3d8d; margin-bottom: 20px;"></div>

    <table style="width:100%; border:none; margin-bottom: 20px;">
        <tr>
            <td style="border:none; width: 50%;">
                <p style="margin:0; color: #777; text-transform: uppercase; font-size: 12px;">Ditujukan Kepada:</p>
                <h3 style="margin:5px 0;">{str(d['Pengirim']).upper()}</h3>
            </td>
            <td style="border:none; text-align:right; width: 50%;">
                <p style="margin:0;"><strong>Tanggal Pengiriman:</strong> {d['Tanggal']}</p>
                <p style="margin:0;"><strong>Metode:</strong> Darat / Laut</p>
            </td>
        </tr>
    </table>

    <table style="width:100%; border-collapse: collapse; text-align: center; border: 1px solid #ddd;">
        <thead>
            <tr style="background-color: #1a3d8d; color: white;">
                <th style="border: 1px solid #1a3d8d; padding:12px;">Deskripsi Barang</th>
                <th style="border: 1px solid #1a3d8d; padding:12px;">Origin</th>
                <th style="border: 1px solid #1a3d8d; padding:12px;">Destination</th>
                <th style="border: 1px solid #1a3d8d; padding:12px;">Kolli</th>
                <th style="border: 1px solid #1a3d8d; padding:12px;">Berat</th>
                <th style="border: 1px solid #1a3d8d; padding:12px;">Harga Satuan</th>
                <th style="border: 1px solid #1a3d8d; padding:12px;">Total</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ddd; padding:15px; text-align: left;">{d['Produk']}</td>
                <td style="border: 1px solid #ddd; padding:15px;">{d['Origin']}</td>
                <td style="border: 1px solid #ddd; padding:15px;">{d['Destination']}</td>
                <td style="border: 1px solid #ddd; padding:15px;">{v_kolli}</td>
                <td style="border: 1px solid #ddd; padding:15px;">{v_berat} Kg</td>
                <td style="border: 1px solid #ddd; padding:15px;">Rp {harga_float:,.0f}</td>
                <td style="border: 1px solid #ddd; padding:15px; font-weight: bold;">Rp {total_float:,.0f}</td>
            </tr>
        </tbody>
    </table>

    <div style="margin-top: 20px; text-align: right;">
        <table style="float: right; width: 40%; border-collapse: collapse;">
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 10px; border: 1px solid #ddd;"><strong>TOTAL TAGIHAN</strong></td>
                <td style="padding: 10px; border: 1px solid #ddd; font-size: 18px; color: #d62828; font-weight: bold;">Rp {total_float:,.0f}</td>
            </tr>
        </table>
        <div style="clear: both;"></div>
    </div>

    <div style="margin-top: -10px; padding: 10px; background-color: #f2f2f2; border-radius: 5px; border-left: 5px solid #d62828;">
        <p style="margin:0; font-style: italic;"><strong>Terbilang:</strong> {terbilang(total_float)} Rupiah</p>
    </div>

    <br>

    <table style="width:100%; border:none; margin-top: 30px;">
        <tr>
            <td style="width:55%; border:none; vertical-align: top; font-size: 13px;">
                <div style="color: #1a3d8d; font-weight: bold; margin-bottom: 5px; border-bottom: 1px solid #1a3d8d; display: inline-block;">INFORMASI PEMBAYARAN</div>
                <br>Bank Central Asia (BCA)<br>
                Nomor Rekening: <strong>6720422334</strong><br>
                Atas Nama: <strong>ADITYA GAMA SAPUTRI</strong><br>
                <p style="font-size: 11px; color: #666; margin-top: 10px;">
                    * Mohon sertakan nomor resi saat melakukan transfer.<br>
                    * Konfirmasi pembayaran ke Finance: 082179799200
                </p>
            </td>
            <td style="text-align: center; border:none; position: relative; width: 45%;">
                <p style="margin-bottom: 80px;">Gresik, {d['Tanggal']}<br>Hormat Kami,</p>
                <div style="position: relative; display: inline-block;">
                    <img src="data:image/png;base64,{stempel}" style="width:220px; opacity: 0.9;">
                    <img src="data:image/png;base64,{ttd}" style="width:130px; position: absolute; top: 10px; left: 50%; transform: translateX(-50%); z-index: 10;">
                </div>
                <p style="margin-top: 10px; font-weight: bold; text-decoration: underline;">PT. GAMA GEMAH GEMILANG</p>
            </td>
        </tr>
    </table>
</div>
""", unsafe_allow_html=True)










