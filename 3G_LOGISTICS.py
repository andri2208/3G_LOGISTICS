import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
import requests
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="3G LOGISTICS - System",
    page_icon="3G.png",
    layout="wide"
)

# --- 2. SETTING URL (PASTIKAN SUDAH BENAR) ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzXgo5VKAEzx3WhjB4RIq91oG-N5dKA3sAHGCTNaUOj_f6CGRDHSe12UOL9aZYCuKk_/exec"

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
    return conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)

# --- 5. HEADER ---
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
            harga = st.number_input("Harga Satuan", min_value=0, step=1)
            berat = st.number_input("Berat (Kg)", min_value=0.0, step=0.1)
        
        submit = st.form_submit_button("Simpan ke Google Sheets")
        
        if submit:
            payload = {
                "Tanggal": tgl.strftime('%d-%b-%y'),
                "Resi": str(resi),
                "Pengirim": str(pengirim),
                "Produk": str(produk),
                "Origin": str(origin),
                "Destination": str(dest),
                "Kolli": int(kolli),
                "Harga": int(harga),
                "Berat": float(berat)
            }
            try:
                resp = requests.post("https://script.google.com/macros/s/AKfycbzXgo5VKAEzx3WhjB4RIq91oG-N5dKA3sAHGCTNaUOj_f6CGRDHSe12UOL9aZYCuKk_/exec", json=payload)
                if resp.status_code == 200:
                    st.success("✅ Data Berhasil Disimpan!")
                    st.cache_data.clear()
                else:
                    st.error("Gagal mengirim ke Apps Script.")
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.subheader("Data Logistik")
    df_db = fetch_data()
    st.dataframe(df_db, use_container_width=True)

with tab3:
    df_inv = fetch_data()
    if not df_inv.empty:
        df_inv.columns = df_inv.columns.str.strip()
        pilih_resi = st.selectbox("Cari Nomor Resi", df_inv['Resi'].dropna().unique())
        
        # Filter Data
        d = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
        
        # --- KALKULASI HARGA UTUH (Anti Desimal Salah) ---
        raw_h = str(d.get('Harga', '0'))
        # Menghapus karakter titik/koma agar 4.000 menjadi 4000
        clean_h = "".join(filter(str.isdigit, raw_h.split('.')[0]))
        
        h_val = float(clean_h) if clean_h else 0.0
        b_val = float(pd.to_numeric(d.get('Berat', 0), errors='coerce'))
        total_float = h_val * b_val

        # --- TEMPLATE INVOICE ---
        st.markdown(f"""
        <div style="border: 1px solid #000; padding: 40px; background-color: white; color: black; font-family: Arial, sans-serif;">
            <table style="width:100%; border:none;">
                <tr>
                    <td style="width:110px; border:none; vertical-align: middle;">
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
                        <p style="margin:0; font-weight: bold;"># {d.get('Resi', '-')}</p>
                    </td>
                </tr>
            </table>
            <hr style="border: none; border-top: 3px solid #1a3d8d; margin: 15px 0;">
            <table style="width:100%; border-collapse: collapse; text-align: center; border: 1px solid black;">
                <tr style="background-color: #1a3d8d; color: white;">
                    <th style="border: 1px solid black; padding:10px;">Item</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Dest</th>
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
                <h3 style="margin:0; color: #d62828;">TAGIHAN: Rp {total_float:,.0f}</h3>
            </div>
            <div style="margin-top: 10px; padding: 10px; background-color: #f5f5f5; border-left: 5px solid #d62828;">
                <strong>Terbilang:</strong> <em>{terbilang(total_float)} Rupiah</em>
            </div>
            <table style="width:100%; border:none; margin-top: 40px;">
                <tr>
                    <td style="width:60%; border:none; vertical-align: top; font-size: 13px;">
                        <strong>TRANSFER:</strong><br>
                        BCA: 6720422334 / ADITYA GAMA SAPUTRI
                    </td>
                    <td style="text-align: center; border:none;">
                        Gresik, {d.get('Tanggal','-')}<br>
                        <strong>PT. GAMA GEMAH GEMILANG</strong><br><br>
                        <div style="position: relative; display: inline-block;">
                            <img src="data:image/png;base64,{stempel_base}" style="width:140px;">
                            <img src="data:image/png;base64,{ttd_base}" style="width:90px; position: absolute; top: 10px; left: 25px;">
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Database kosong.")
