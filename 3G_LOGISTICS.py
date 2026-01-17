import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# Link Apps Script & Spreadsheet Anda
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw9le3yTcQn3TAevrbOi1s7X-wGJKd-o7n1lN4o8yp7KvmOAHX9GhoGLU8x67IrZWDl/exec"

def get_image_base64(path):
    import os
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_base = get_image_base64("3G.png")
stempel_base = get_image_base64("STEMPEL.png")

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

conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

tab1, tab2, tab3 = st.tabs(["➕ Input Data", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("No Resi (Contoh: 3G-0001)")
            pengirim = st.text_input("Customer (Contoh: BAPAK ANDI)")
            produk = st.text_area("Deskripsi Barang")
        with col2:
            org = st.text_input("Origin (Contoh: SBY)")
            dst = st.text_input("Destination (Contoh: MEDAN)")
            kolli = st.number_input("KOLLI", min_value=1, step=1)
            harga = st.number_input("Harga Satuan", min_value=0, step=500)
            berat = st.number_input("Berat/Weight (Kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("SIMPAN"):
            payload = {
                "Tanggal": tgl.strftime('%d-%b-%y'), "Resi": resi, "Pengirim": pengirim,
                "Produk": produk, "Origin": org, "Destination": dst,
                "Kolli": str(int(kolli)), "Harga": str(int(harga)), "Berat": str(float(berat))
            }
            res = requests.post(APPS_SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("Data Berhasil Disimpan!")
                st.cache_data.clear()

with tab2:
    df = fetch_data()
    st.dataframe(df, use_container_width=True)

with tab3:
    df_inv = fetch_data()
    if not df_inv.empty and 'Resi' in df_inv.columns:
        pilih = st.selectbox("Pilih No Resi", df_inv['Resi'].dropna().unique())
        d = df_inv[df_inv['Resi'] == pilih].iloc[0]
        
        # LOGIKA HARGA ANTI-40
        h_raw = str(d.get('Harga', '0')).split('.')[0]
        h_fix = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
        b_val = float(pd.to_numeric(d.get('Berat', 0), errors='coerce'))
        total = h_fix * b_val

        st.markdown(f"""
        <div style="background-color: white; color: black; padding: 40px; border: 1px solid #ccc; font-family: sans-serif;">
            <table style="width: 100%; border: none;">
                <tr>
                    <td style="width: 15%;"><img src="data:image/png;base64,{logo_base}" width="100"></td>
                    <td style="width: 60%;">
                        <h2 style="margin: 0; color: #1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size: 12px; margin: 0;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>Telp 031-79973432 | Email: finance@3glogistics.com</p>
                    </td>
                    <td style="text-align: right;">
                        <h1 style="margin: 0; color: red;">INVOICE</h1>
                        <p style="margin: 0;"><b>DATE: {d.get('Tanggal','')}</b></p>
                    </td>
                </tr>
            </table>
            <hr style="border-top: 2px solid #1a3d8d;">
            <p style="margin: 20px 0;"><b>CUSTOMER: {str(d.get('Pengirim','')).upper()}</b></p>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1px solid black;">Product Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">KOLLI</th>
                    <th style="border: 1px solid black;">HARGA</th>
                    <th style="border: 1px solid black;">WEIGHT</th>
                    <th style="border: 1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 15px;">{d.get('Tanggal','')}</td>
                    <td style="border: 1px solid black;">{d.get('Produk','')}</td>
                    <td style="border: 1px solid black;">{d.get('Origin','')}</td>
                    <td style="border: 1px solid black;">{d.get('Destination','')}</td>
                    <td style="border: 1px solid black;">{d.get('Kolli',0)}</td>
                    <td style="border: 1px solid black;">Rp {h_fix:,}</td>
                    <td style="border: 1px solid black;">{b_val} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total:,.0f}</td>
                </tr>
            </table>
            <div style="text-align: right; margin-top: 20px;">
                <h3 style="margin: 0;">YANG HARUS DI BAYAR: <span style="color: red;">Rp {total:,.0f}</span></h3>
                <p><i>Terbilang: {terbilang(total)} Rupiah</i></p>
            </div>
            <table style="width: 100%; margin-top: 40px;">
                <tr>
                    <td style="width: 60%; font-size: 12px;">
                        <b>TRANSFER TO:</b><br>Bank Central Asia (BCA)<br>No Rek: 6720422334<br>A/N ADITYA GAMA SAPUTRI<br>
                        <br><i>NB: Mohon konfirmasi ke Finance 082179799200 jika sudah transfer.</i>
                    </td>
                    <td style="text-align: center;">
                        Gresik, {d.get('Tanggal','')}<br>Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br><br><br>
                        <b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
