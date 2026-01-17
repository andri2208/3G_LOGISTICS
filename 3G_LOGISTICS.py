import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", layout="wide")

# CSS untuk hasil cetak yang bersih
st.markdown("""
    <style>
    @media print {
        header, .stSidebar, .stTabs [data-baseweb="tab-list"], .stActionButton, button { display: none !important; }
        .main .block-container { padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONFIG URL & KONEKSI ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw9le3yTcQn3TAevrbOi1s7X-wGJKd-o7n1lN4o8yp7KvmOAHX9GhoGLU8x67IrZWDl/exec"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_image_base64(path):
    import os
    import base64
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

# Load Gambar-gambar
logo_base = get_image_base64("3G.png")
ttd_base = get_image_base64("TANDA TANGAN.png")
stempel_base = get_image_base64("STEMPEL DAN NAMA.png")

def fetch_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

# --- 3. UI TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Input Data", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("No Resi")
            customer = st.text_input("Customer Name")
            produk = st.text_area("Product Description")
        with col2:
            org = st.text_input("Origin")
            dst = st.text_input("Destination")
            kolli = st.number_input("KOLLI", min_value=1, step=1)
            harga = st.number_input("Harga Satuan", min_value=0)
            berat = st.number_input("Weight (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN DATA"):
            payload = {
                "Tanggal": tgl.strftime('%d-%b-%y'), "Resi": resi, "Pengirim": customer,
                "Produk": produk, "Origin": org, "Destination": dst,
                "Kolli": str(int(kolli)), "Harga": str(int(harga)), "Berat": str(float(berat))
            }
            try:
                res = requests.post(APPS_SCRIPT_URL, json=payload)
                if res.status_code == 200:
                    st.success("Data Berhasil Disimpan!")
                    st.cache_data.clear()
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.dataframe(fetch_data(), use_container_width=True)

with tab3:
    df_inv = fetch_data()
    if not df_inv.empty and 'Resi' in df_inv.columns:
        pilih = st.selectbox("Pilih No Resi", df_inv['Resi'].dropna().unique())
        d = df_inv[df_inv['Resi'] == pilih].iloc[0]
        
        # --- PERHITUNGAN ---
        h_raw = str(d.get('Harga', '0')).split('.')[0]
        h_fix = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
        b_val = float(pd.to_numeric(d.get('Berat', 0), errors='coerce'))
        total = h_fix * b_val

        # --- LOAD GAMBAR ---
        logo_base = get_image_base64("3G.png")
        ttd_base = get_image_base64("TANDA TANGAN.png")
        stempel_base = get_image_base64("STEMPEL DAN NAMA.png")

        # --- HTML INVOICE (Variabel didefinisikan di sini) ---
        html_cetak = f"""
        <div style="background-color: white; color: black; padding: 30px; border: 1px solid #eee; font-family: Arial;">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 150px;"><img src="data:image/png;base64,{logo_base}" width="130"></td>
                    <td>
                        <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>Telp 031-79973432</p>
                    </td>
                    <td style="text-align:right;">
                        <h1 style="margin:0; color:red;">INVOICE</h1>
                        <p><b>DATE: {d.get('Tanggal','')}</b></p>
                    </td>
                </tr>
            </table>
            <hr style="border:2px solid #1a3d8d;">
            <p><b>CUSTOMER: {str(d.get('Pengirim','')).upper()}</b></p>
            
            <table style="width:100%; border-collapse:collapse; border:1px solid black; text-align:center; font-size:12px;">
                <tr style="background-color:#f2f2f2;">
                    <th style="border:1px solid black; padding:8px;">Date of Load</th>
                    <th style="border:1px solid black;">Product Description</th>
                    <th style="border:1px solid black;">Origin</th>
                    <th style="border:1px solid black;">Destination</th>
                    <th style="border:1px solid black;">KOLLI</th>
                    <th style="border:1px solid black;">HARGA</th>
                    <th style="border:1px solid black;">WEIGHT</th>
                    <th style="border:1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:15px;">{d.get('Tanggal','')}</td>
                    <td style="border:1px solid black; text-align:left; padding-left:5px;">{d.get('Produk','')}</td>
                    <td style="border:1px solid black;">{d.get('Origin','')}</td>
                    <td style="border:1px solid black;">{d.get('Destination','')}</td>
                    <td style="border:1px solid black;">{d.get('Kolli',0)}</td>
                    <td style="border:1px solid black;">Rp {h_fix:,}</td>
                    <td style="border:1px solid black;">{b_val} Kg</td>
                    <td style="border:1px solid black; font-weight:bold;">Rp {total:,.0f}</td>
                </tr>
            </table>

            <div style="text-align:right; margin-top:20px;">
                <h3>YANG HARUS DI BAYAR: <span style="color:red;">Rp {total:,.0f}</span></h3>
                <p><i>Terbilang: {terbilang(total)} Rupiah</i></p>
            </div>

            <table style="width:100%; margin-top:30px;">
                <tr>
                    <td style="width:60%; font-size:12px;">
                        <b>TRANSFER TO :</b><br>Bank BCA | No Rek: 6720422334<br>A/N ADITYA GAMA SAPUTRI
                    </td>
                    <td style="text-align:center; position:relative;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        <div style="position:relative; height:100px; margin-top:10px;">
                            <img src="data:image/png;base64,{ttd_base}" style="position:absolute; width:100px; left:50%; transform:translateX(-50%); z-index:1;">
                            <img src="data:image/png;base64,{stempel_base}" style="position:absolute; width:150px; left:50%; transform:translateX(-50%); top:-10px; z-index:2; opacity:0.8;">
                        </div>
                        <br><b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # --- PEMANGGILAN (Pastikan variabelnya sama: html_cetak) ---
        st.markdown(html_cetak, unsafe_allow_html=True)

