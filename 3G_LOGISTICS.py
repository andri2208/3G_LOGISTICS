import streamlit as st
import pandas as pd
import requests

# Konfigurasi Halaman & Judul Tab
st.set_page_config(page_title="Sistem Invoice 3G Logistics", page_icon="🚚", layout="centered")

# URL API Google Apps Script kamu
API_URL = "ISI_DENGAN_URL_WEB_APP_KAMU"

# Fungsi Konversi Angka ke Terbilang
def terbilang(n):
    bilangan = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    if n < 12:
        return bilangan[int(n)]
    elif n < 20:
        return terbilang(n - 10) + " belas"
    elif n < 100:
        return terbilang(n // 10) + " puluh " + terbilang(n % 10)
    elif n < 200:
        return " seratus " + terbilang(n - 100)
    elif n < 1000:
        return terbilang(n // 100) + " ratus " + terbilang(n % 100)
    elif n < 2000:
        return " seribu " + terbilang(n - 1000)
    elif n < 1000000:
        return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    return ""

def get_data():
    try:
        response = requests.get(API_URL, timeout=10)
        return response.json()
    except:
        return []

# --- TAMPILAN SIDEBAR ---
st.sidebar.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", width=100)
st.sidebar.header("Navigasi")

data_json = get_data()

if not data_json:
    st.error("Gagal terhubung ke Database Google Sheets. Pastikan URL API benar.")
else:
    df = pd.DataFrame(data_json)
    
    # Pilih Customer
    customer_list = df['customer'].unique()
    selected_customer = st.sidebar.selectbox("Pilih Nama Customer", customer_list)
    
    # Ambil data spesifik customer tersebut
    inv = df[df['customer'] == selected_customer].iloc[0]
    total_bayar = int(inv['total'])
    teks_terbilang = terbilang(total_bayar).title() + " Rupiah"

    # --- RENDER INVOICE (HTML/CSS) ---
    st.markdown(f"""
    <div style="background-color: white; padding: 30px; border: 1px solid #ccc; color: black; font-family: 'Arial';">
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width: 100%;">
        </div>
        
        <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold;">
            INVOICE
        </div>
        
        <table style="width: 100%; font-size: 14px; margin-bottom: 10px;">
            <tr>
                <td><b>CUSTOMER : {inv['customer']}</b></td>
                <td style="text-align: right;"><b>DATE : {inv['date']}</b></td>
            </tr>
        </table>

        <table style="width: 100%; border-collapse: collapse; border: 1px solid black; font-size: 12px; text-align: center;">
            <tr style="background-color: #4A90E2; color: white;">
                <th style="border: 1px solid black; padding: 8px;">Date of Load</th>
                <th style="border: 1px solid black;">Product Description</th>
                <th style="border: 1px solid black;">Origin</th>
                <th style="border: 1px solid black;">Destination</th>
                <th style="border: 1px solid black;">KOLLI</th>
                <th style="border: 1px solid black;">HARGA</th>
                <th style="border: 1px solid black;">WEIGHT</th>
            </tr>
            <tr>
                <td style="border: 1px solid black; padding: 10px;">{inv['date']}</td>
                <td style="border: 1px solid black;">{inv['description']}</td>
                <td style="border: 1px solid black;">{inv['origin']}</td>
                <td style="border: 1px solid black;">{inv['destination']}</td>
                <td style="border: 1px solid black;">{inv['kolli']}</td>
                <td style="border: 1px solid black;">Rp {int(inv['harga']):,}</td>
                <td style="border: 1px solid black;">{inv['weight']} Kg</td>
            </tr>
            <tr style="font-weight: bold;">
                <td colspan="6" style="border: 1px solid black; text-align: center; background-color: #eee;">YANG HARUS DI BAYAR</td>
                <td style="border: 1px solid black;">Rp {total_bayar:,}</td>
            </tr>
        </table>
        
        <div style="border: 1px solid black; margin-top: 5px; padding: 5px; font-size: 12px; font-style: italic;">
            <b>Terbilang :</b> {teks_terbilang}
        </div>

        <div style="margin-top: 20px; display: flex; justify-content: space-between; font-size: 13px;">
            <div>
                <b>TRANSFER TO :</b><br>
                Bank Central Asia<br>
                6720422334<br>
                A/N ADITYA GAMA SAPUTRI<br>
                <small>NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</small>
            </div>
            <div style="text-align: center;">
                Sincerely,<br>
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width: 150px;"><br>
                <b><u>KELVINITO JAYADI</u></b><br>
                DIREKTUR
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.button("Cetak Invoice (Ctrl + P)")
