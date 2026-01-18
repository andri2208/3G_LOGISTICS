import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G Logistics Invoice System", page_icon="🚚", layout="wide")

# URL API Google Apps Script Anda
API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# --- FUNGSI TERBILANG ---
def terbilang(n):
    bilangan = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " belas"
    elif n < 100: return terbilang(n // 10) + " puluh " + terbilang(n % 10)
    elif n < 200: return " seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " ratus " + terbilang(n % 100)
    elif n < 2000: return " seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    return ""

# --- FUNGSI AMBIL DATA ---
@st.cache_data(ttl=60) # Cache data selama 1 menit agar lebih cepat
def get_data():
    try:
        response = requests.get(API_URL, timeout=15)
        return response.json()
    except:
        return []

# --- ANTARMUKA UTAMA ---
st.title("🚚 3G Logistics System")

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data Baru"])

with tab1:
    data_json = get_data()
    
    if not data_json:
        st.error("Koneksi Database Gagal. Periksa URL Apps Script Anda.")
    else:
        df = pd.DataFrame(data_json)
        
        # Sidebar Filter
        st.sidebar.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", width=80)
        customer_list = df['customer'].unique()
        selected_customer = st.sidebar.selectbox("Cari Nama Customer", customer_list)
        
        # Ambil data customer (paling baru)
        inv = df[df['customer'] == selected_customer].iloc[-1]
        
        # Bersihkan Tanggal
        tgl_raw = str(inv['date']).split('T')[0]
        total_bayar = int(inv['total'])
        teks_terbilang = terbilang(total_bayar).title() + " Rupiah"

        # --- BAGIAN HTML (Sesuai image_389d67.png) ---
        # Pastikan variabel ini didefinisikan dengan rapi
        invoice_template = f"""
<div style="background-color: white; padding: 20px; border: 1px solid black; color: black; font-family: sans-serif; line-height: 1.4;">
    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width: 100%; margin-bottom: 10px;">
    
    <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 18px;">
        INVOICE
    </div>
    
    <table style="width: 100%; font-size: 14px; margin-bottom: 10px;">
        <tr>
            <td style="text-align: left;"><b>CUSTOMER : {inv['customer']}</b></td>
            <td style="text-align: right;"><b>DATE : {tgl_raw}</b></td>
        </tr>
    </table>

    <table style="width: 100%; border-collapse: collapse; border: 1px solid black; font-size: 12px; text-align: center;">
        <tr style="background-color: #316395; color: white;">
            <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
            <th style="border: 1px solid black;">Product Description</th>
            <th style="border: 1px solid black;">Origin</th>
            <th style="border: 1px solid black;">Destination</th>
            <th style="border: 1px solid black;">KOLLI</th>
            <th style="border: 1px solid black;">HARGA</th>
            <th style="border: 1px solid black;">WEIGHT</th>
        </tr>
        <tr>
            <td style="border: 1px solid black; padding: 12px;">{tgl_raw}</td>
            <td style="border: 1px solid black;">{inv['description']}</td>
            <td style="border: 1px solid black;">{inv['origin']}</td>
            <td style="border: 1px solid black;">{inv['destination']}</td>
            <td style="border: 1px solid black;">{inv['kolli']}</td>
            <td style="border: 1px solid black;">Rp {int(inv['harga']):,}</td>
            <td style="border: 1px solid black;">{inv['weight']} Kg</td>
        </tr>
        <tr style="font-weight: bold; background-color: #f2f2f2;">
            <td colspan="6" style="border: 1px solid black; text-align: center; padding: 8px;">YANG HARUS DI BAYAR</td>
            <td style="border: 1px solid black;">Rp {total_bayar:,}</td>
        </tr>
    </table>
    
    <div style="border: 1px solid black; margin-top: 5px; padding: 8px; font-size: 13px; font-style: italic; background-color: #f9f9f9;">
        <b>Terbilang :</b> {teks_terbilang}
    </div>

    <div style="margin-top: 25px; display: flex; justify-content: space-between; font-size: 12px;">
        <div style="width: 60%;">
            <b>TRANSFER TO :</b><br>
            Bank Central Asia<br>
            6720422334<br>
            A/N ADITYA GAMA SAPUTRI<br>
            <small>NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</small>
        </div>
        <div style="text-align: center; width: 40%;">
            Sincerely,<br>
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width: 140px;"><br>
            <b><u>KELVINITO JAYADI</u></b><br>
            DIREKTUR
        </div>
    </div>
</div>
"""
        # EKSEKUSI RENDER HTML
        st.markdown(invoice_template, unsafe_allow_html=True)
        st.write("") 
        st.button("🖨️ Cetak ke PDF (Ctrl+P)")

with tab2:
    st.subheader("Input Data Baru")
    with st.form("form_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            in_tgl = st.date_input("Tanggal", datetime.now())
            in_cust = st.text_input("Customer")
            in_desc = st.text_input("Produk")
        with c2:
            in_orig = st.text_input("Origin")
            in_dest = st.text_input("Destination")
            in_weight = st.number_input("Weight (Kg)", min_value=1)
            in_harga = st.number_input("Harga/Kg", min_value=0)
        
        btn_save = st.form_submit_button("Kirim ke Database")
        
        if btn_save:
            payload = {
                "date": in_tgl.strftime("%Y-%m-%d"),
                "customer": in_cust.upper(),
                "description": in_desc.upper(),
                "origin": in_orig.upper(),
                "destination": in_dest.upper(),
                "kolli": 0,
                "harga": in_harga,
                "weight": in_weight,
                "total": in_harga * in_weight
            }
            res = requests.post(API_URL, data=json.dumps(payload))
            if res.status_code == 200:
                st.success("Data Berhasil Disimpan!")
                st.cache_data.clear() # Hapus cache agar data baru langsung muncul
