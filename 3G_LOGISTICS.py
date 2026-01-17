import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import requests
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="3G LOGISTICS - Management System",
    page_icon="3G.png",
    layout="wide"
)

# --- 2. SETTING URL (GANTI DI SINI) ---
# URL Spreadsheet untuk MEMBACA data
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
# URL Web App Apps Script untuk MENYIMPAN data
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzfUoRYoJzuMg3KsbXUObTdHQOu9vBWvh38lTiao2PktjxIS4-6JG5OrWU52klEOiLU/exec"

# --- 3. FUNGSI TOOLS ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return str(int(n))

# Load Assets
logo_base = get_image_base64("3G.png")
stempel_base = get_image_base64("STEMPEL.png")
ttd_base = get_image_base64("TTD.png")

# --- 4. KONEKSI DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    # ttl=0 memastikan data selalu fresh saat pindah tab
    return conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)

# --- 5. TAMPILAN HEADER ---
st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px;">
        <img src="data:image/png;base64,{logo_base}" width="80">
        <div>
            <h1 style="margin: 0; color: #1a3d8d; font-size: 28px;">PT. GAMA GEMAH GEMILANG</h1>
            <p style="margin: 0; color: #d62828; font-weight: bold;">Logistics Management System</p>
        </div>
    </div>
    <hr style="border-top: 3px solid #1a3d8d; margin-bottom: 30px;">
""", unsafe_allow_html=True)

# --- 6. TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Tambah Data", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("Nomor Resi")
            pengirim = st.text_input("Nama Customer")
            produk = st.text_input("Deskripsi Barang")
        with col2:
            origin = st.text_input("Origin")
            dest = st.text_input("Destination")
            kolli = st.number_input("Kolli", min_value=1, step=1)
            harga = st.number_input("Harga Satuan", min_value=0, step=1000)
            berat = st.number_input("Berat (Kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Simpan ke Google Sheets"):
            payload = {
                "Tanggal": tgl.strftime('%d-%b-%y'),
                "Resi": resi,
                "Pengirim": pengirim,
                "Produk": produk,
                "Origin": origin,
                "Destination": dest,
                "Kolli": int(kolli),
                "Harga": int(harga),
                "Berat": float(berat)
            }
            try:
                # Mengirim data ke Apps Script
                resp = requests.post("https://script.google.com/macros/s/AKfycbzfUoRYoJzuMg3KsbXUObTdHQOu9vBWvh38lTiao2PktjxIS4-6JG5OrWU52klEOiLU/exec", json=payload)
                if resp.status_code == 200:
                    st.success("✅ Data berhasil masuk ke Google Sheets!")
                    st.cache_data.clear() # Reset cache agar Tab 2 & 3 langsung update
                else:
                    st.error("Gagal mengirim. Pastikan URL Apps Script benar dan sudah di-Deploy sebagai 'Anyone'.")
            except Exception as e:
                st.error(f"Error Koneksi: {e}")

with tab2:
    st.subheader("Data Logistik")
    df_db = fetch_data()
    st.dataframe(df_db, use_container_width=True)

with tab3:
    df_inv = fetch_data()
    if not df_inv.empty:
        # Menghapus spasi nama kolom untuk keamanan
        df_inv.columns = df_inv.columns.str.strip()
        
        pilih_resi = st.selectbox("Cari Nomor Resi", df_inv['Resi'].dropna().unique())
        
        # Filter Data
        d = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
        
        # Kalkulasi
        try:
            h_val = float(d.get('Harga', 0))
            b_val = float(d.get('Berat', 0))
            total_float = h_val * b_val
        except:
            total_float = 0

        # --- TEMPLATE INVOICE ---
        st.markdown(f"""
        <div style="border: 1px solid #000; padding: 40px; background-color: white; color: black; font-family: Arial, sans-serif;">
            <table style="width:100%; border:none;">
                <tr>
                    <td style="width:120px; border:none; vertical-align: middle;">
                        <img src="data:image/png;base64,{logo_base}" style="width:100px;">
                    </td>
                    <td style="border:none; padding-left: 15px; vertical-align: middle;">
                        <h2 style="margin:0; color: #1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:2px 0;">
                            Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti,<br>
                            Gresik, Jawa Timur. Telp: 031-79973432 | Email: finance@3glogistics.com
                        </p>
                    </td>
                    <td style="border:none; text-align:right; vertical-align: middle;">
                        <h1 style="margin:0; color: #d62828; font-size: 30px;">INVOICE</h1>
                        <p style="margin:0; font-weight: bold;">No. Resi: {d.get('Resi', '-')}</p>
                    </td>
                </tr>
            </table>
            
            <hr style="border: none; border-top: 3px solid #1a3d8d; margin: 15px 0;">
            
            <table style="width:100%; border:none; margin-bottom: 20px;">
                <tr>
                    <td style="border:none;"><strong>CUSTOMER:</strong><br>{str(d.get('Pengirim','-')).upper()}</td>
                    <td style="text-align:right; border:none;"><strong>TANGGAL:</strong> {d.get('Tanggal','-')}</td>
                </tr>
            </table>

            <table style="width:100%; border-collapse: collapse; text-align: center; border: 1px solid black;">
                <tr style="background-color: #1a3d8d; color: white;">
                    <th style="border: 1px solid black; padding:10px;">Deskripsi Barang</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">Kolli</th>
                    <th style="border: 1px solid black;">Berat</th>
                    <th style="border: 1px solid black;">Harga</th>
                    <th style="border: 1px solid black;">Total</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding:15px; text-align: left;">{d.get('Produk','-')}</td>
                    <td style="border: 1px solid black;">{d.get('Origin','-')}</td>
                    <td style="border: 1px solid black;">{d.get('Destination','-')}</td>
                    <td style="border: 1px solid black;">{d.get('Kolli',0)}</td>
                    <td style="border: 1px solid black;">{d.get('Berat',0)} Kg</td>
                    <td style="border: 1px solid black;">Rp {h_val:,.0f}</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total_float:,.0f}</td>
                </tr>
            </table>
            
            <div style="margin-top: 20px; text-align: right;">
                <h3 style="margin:0; color: #d62828;">TOTAL TAGIHAN: Rp {total_float:,.0f}</h3>
            </div>
            
            <div style="margin-top: 10px; padding: 10px; background-color: #f5f5f5; border-left: 5px solid #d62828;">
                <strong>Terbilang:</strong> <em>{terbilang(total_float)} Rupiah</em>
            </div>

            <table style="width:100%; border:none; margin-top: 40px;">
                <tr>
                    <td style="width:60%; border:none; vertical-align: top; font-size: 13px;">
                        <strong>PEMBAYARAN TRANSFER:</strong><br>
                        Bank Central Asia (BCA)<br>
                        No. Rekening: <strong>6720422334</strong><br>
                        A/N: <strong>ADITYA GAMA SAPUTRI</strong>
                    </td>
                    <td style="text-align: center; border:none;">
                        Hormat Kami,<br>
                        <strong>PT. GAMA GEMAH GEMILANG</strong><br><br>
                        <div style="position: relative; display: inline-block; height: 110px;">
                            <img src="data:image/png;base64,{stempel_base}" style="width:160px; opacity: 0.85;">
                            <img src="data:image/png;base64,{ttd_base}" style="width:100px; position: absolute; top: 10px; left: 30px;">
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Database kosong, silakan isi data terlebih dahulu.")
