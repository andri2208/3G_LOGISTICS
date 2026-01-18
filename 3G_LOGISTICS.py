import streamlit as st
import pandas as pd
import requests

# Konfigurasi Halaman
st.set_page_config(layout="wide")

# Masukkan URL dari Google Apps Script Anda di sini
API_URL = "https://script.google.com/macros/s/AKfycbwchICNuVh5xlgMYlEtqeVxZypUYlg0nNe03tRwVhu5DmN6YR02-6Wsuagi2tUiZ_HF/exec"

def get_data():
    response = requests.get(API_URL)
    return response.json()

st.title("🚚 Logistic Invoice Generator")

try:
    data = get_data()
    df = pd.DataFrame(data)

    # Sidebar untuk memilih invoice berdasarkan Nama Customer atau Tanggal
    customer_list = df['customer'].unique()
    selected_customer = st.sidebar.selectbox("Pilih Customer", customer_list)

    # Filter data berdasarkan pilihan
    invoice_data = df[df['customer'] == selected_customer].iloc[0]

    # --- Tampilan Invoice (Template HTML) ---
    invoice_html = f"""
    <div style="border: 2px solid black; padding: 20px; font-family: Arial, sans-serif;">
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="width: 30%;"><h2 style="color: blue;">BG</h2></td>
                <td style="text-align: left;">
                    <b style="color: blue;">PT. GAMA GEMAH GEMILANG</b><br>
                    <small>Ruko Paragon Plaza Blok D - 6 Jalan Ngasinan, Menganti, Gresik. Telp 031-79973432</small>
                </td>
            </tr>
        </table>
        
        <div style="text-align: center; border-top: 1px solid black; border-bottom: 1px solid black; margin: 10px 0; padding: 5px;">
            <b>INVOICE</b>
        </div>
        
        <table style="width: 100%; margin-bottom: 10px;">
            <tr>
                <td>CUSTOMER : {invoice_data['customer']}</td>
                <td style="text-align: right;">DATE : {invoice_data['date']}</td>
            </tr>
        </table>

        <table style="width: 100%; border: 1px solid black; border-collapse: collapse; text-align: center;">
            <tr style="background-color: #4A90E2; color: white;">
                <th style="border: 1px solid black;">Date of Load</th>
                <th style="border: 1px solid black;">Product Description</th>
                <th style="border: 1px solid black;">Origin</th>
                <th style="border: 1px solid black;">Destination</th>
                <th style="border: 1px solid black;">HARGA</th>
                <th style="border: 1px solid black;">WEIGHT</th>
            </tr>
            <tr>
                <td style="border: 1px solid black;">{invoice_data['date']}</td>
                <td style="border: 1px solid black;">{invoice_data['description']}</td>
                <td style="border: 1px solid black;">{invoice_data['origin']}</td>
                <td style="border: 1px solid black;">{invoice_data['destination']}</td>
                <td style="border: 1px solid black;">Rp {invoice_data['harga']:,}</td>
                <td style="border: 1px solid black;">{invoice_data['weight']} Kg</td>
            </tr>
        </table>
        
        <div style="margin-top: 20px;">
            <b>TOTAL YANG HARUS DIBAYAR: Rp {invoice_data['total']:,}</b>
        </div>
    </div>
    """

    st.markdown(invoice_html, unsafe_allow_html=True)
    
    if st.button("Cetak ke PDF"):
        st.info("Gunakan fitur 'Print' (Ctrl+P) pada browser dan simpan sebagai PDF.")

except Exception as e:
    st.error(f"Gagal memuat data: {e}")

