import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIG HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", layout="wide")

st.markdown("""
    <style>
    @media print {
        header, .stSidebar, .stTabs [data-baseweb="tab-list"], .stActionButton, button { display: none !important; }
        .main .block-container { padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONFIG URL ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyKO5MqbpJapc_nH63-vZm-TfIB-ntsC1dmzr32QWOL6DrZ7vyWP966wbumlAj2ZwPr/exec"

# --- 3. FUNGSI PENDUKUNG ---
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

logo_base = get_image_base64("3G.png")
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

# --- 4. TAMPILAN TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Input Baru", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("No Resi")
            cust = st.text_input("Nama Customer")
            prod = st.text_area("Deskripsi Barang")
        with c2:
            org = st.text_input("Origin (Asal)")
            dst = st.text_input("Destination (Tujuan)")
            kol = st.number_input("KOLLI", min_value=1, step=1)
            hrg = st.number_input("Harga Satuan", min_value=0)
            brt = st.number_input("Berat (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN DATA"):
            payload = {
                "Tanggal": tgl.strftime('%d-%b-%y'), "Resi": resi, "Pengirim": cust,
                "Produk": prod, "Origin": org, "Destination": dst,
                "Kolli": str(int(kol)), "Harga": str(int(hrg)), "Berat": str(float(brt))
            }
            res = requests.post(APPS_SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("✅ Berhasil Simpan!")
                st.cache_data.clear()

with tab2:
    st.dataframe(fetch_data(), use_container_width=True)

with tab3:
    df = fetch_data()
    if not df.empty and 'Resi' in df.columns:
        pilih = st.selectbox("Pilih Resi", df['Resi'].dropna().unique())
        d = df[df['Resi'] == pilih].iloc[0]
        
        # Pembersihan Angka
        h_raw = str(d.get('Harga', '0')).split('.')[0]
        h_fix = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
        b_fix = float(pd.to_numeric(d.get('Berat', 0), errors='coerce'))
        total = h_fix * b_fix

        # TAMPILAN INVOICE PRESISI
        invoice_html = f"""
        <div style="background-color: white; color: black; padding: 30px; border: 1px solid #ddd; font-family: Arial, sans-serif;">
            <table style="width: 100%; border: none;">
                <tr>
                    <td style="width: 160px; vertical-align: middle;">
                        <img src="data:image/png;base64,{logo_base}" width="150">
                    </td>
                    <td style="vertical-align: middle; padding-left: 20px;">
                        <h1 style="margin: 0; color: #1a3d8d; font-size: 26px;">PT. GAMA GEMAH GEMILANG</h1>
                        <p style="font-size: 11px; margin: 5px 0 0 0;">
                            Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>
                            Telp 031-79973432 | Email: finance@3glogistics.com
                        </p>
                    </td>
                    <td style="text-align: right; vertical-align: top;">
                        <h1 style="margin: 0; color: #d62828; font-size: 32px;">INVOICE</h1>
                        <p style="margin: 5px 0;"><b>DATE: {d.get('Tanggal','')}</b></p>
                    </td>
                </tr>
            </table>
            <hr style="border: none; border-top: 3px solid #1a3d8d; margin: 15px 0;">
            <p style="font-size: 14px;"><b>CUSTOMER: {str(d.get('Pengirim','')).upper()}</b></p>
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; border: 1px solid black;">
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
                    <td style="border: 1px solid black; text-align: left; padding: 10px;">{d.get('Produk','')}</td>
                    <td style="border: 1px solid black;">{d.get('Origin','')}</td>
                    <td style="border: 1px solid black;">{d.get('Destination','')}</td>
                    <td style="border: 1px solid black;">{d.get('Kolli',0)}</td>
                    <td style="border: 1px solid black;">Rp {h_fix:,}</td>
                    <td style="border: 1px solid black;">{b_fix} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total:,.0f}</td>
                </tr>
            </table>
            <div style="text-align: right; margin-top: 20px;">
                <h3 style="margin: 0;">YANG HARUS DI BAYAR: <span style="color: #d62828;">Rp {total:,.0f}</span></h3>
                <p style="font-size: 13px;"><i>Terbilang: {terbilang(total)} Rupiah</i></p>
            </div>
            <table style="width: 100%; margin-top: 40px; font-size: 12px;">
                <tr>
                    <td><b>TRANSFER TO :</b><br>Bank BCA | No Rek: 6720422334<br>A/N ADITYA GAMA SAPUTRI</td>
                    <td style="text-align: center;">
                        Gresik, {d.get('Tanggal','')}<br>Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br><br><br><b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        st.markdown(invoice_html, unsafe_allow_html=True)
