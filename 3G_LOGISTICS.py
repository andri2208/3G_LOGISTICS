import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G Logistics Invoice System", page_icon="🚚", layout="wide")

# URL API Google Apps Script
API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# --- FUNGSI TERBILANG ---
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

# --- FUNGSI AMBIL DATA ---
def get_data():
    try:
        response = requests.get(API_URL, timeout=15)
        return response.json()
    except Exception:
        return []

# --- TAMPILAN UTAMA ---
st.title("Sistem Logistik PT. GAMA GEMAH GEMILANG")

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data Baru"])

# --- TAB 1: CETAK INVOICE ---
with tab1:
    data_json = get_data()
    
    if not data_json:
        st.error("Koneksi gagal! Pastikan Apps Script sudah di-deploy sebagai 'Anyone'.")
    else:
        df = pd.DataFrame(data_json)
        
        # Sidebar Filter
        st.sidebar.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", width=80)
        customer_list = df['customer'].unique()
        selected_customer = st.sidebar.selectbox("Pilih Nama Customer", customer_list)
        
        # Filter Data
        inv = df[df['customer'] == selected_customer].iloc[-1]
        
        # Format Tanggal (Menghapus format T17:00:00.000Z jika ada)
        tgl_bersih = str(inv['date']).split('T')[0]
        
        # Perhitungan
        total_bayar = int(inv['total'])
        teks_terbilang = terbilang(total_bayar).title() + " Rupiah"

        # TEMPLATE HTML (Sesuai image_4283e1.png)
        invoice_html = f"""
        <div style="background-color: white; padding: 25px; border: 1.5px solid black; color: black; font-family: 'Arial'; max-width: 900px; margin: auto;">
            <div style="text-align: center; margin-bottom: 10px;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width: 100%;">
            </div>
            
            <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 18px; letter-spacing: 2px;">
                INVOICE
            </div>
            
            <table style="width: 100%; font-size: 14px; margin-bottom: 15px; border: none;">
                <tr style="border: none;">
                    <td style="border: none; text-align: left;"><b>CUSTOMER : {inv['customer']}</b></td>
                    <td style="border: none; text-align: right;"><b>DATE : {tgl_bersih}</b></td>
                </tr>
            </table>

            <table style="width: 100%; border-collapse: collapse; border: 1.5px solid black; font-size: 13px; text-align: center;">
                <tr style="background-color: #316395; color: white; font-weight: bold;">
                    <th style="border: 1.5px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1.5px solid black;">Product Description</th>
                    <th style="border: 1.5px solid black;">Origin</th>
                    <th style="border: 1.5px solid black;">Destination</th>
                    <th style="border: 1.5px solid black;">KOLLI</th>
                    <th style="border: 1.5px solid black;">HARGA</th>
                    <th style="border: 1.5px solid black;">WEIGHT</th>
                </tr>
                <tr>
                    <td style="border: 1.5px solid black; padding: 12px;">{tgl_bersih}</td>
                    <td style="border: 1.5px solid black;">{inv['description']}</td>
                    <td style="border: 1.5px solid black;">{inv['origin']}</td>
                    <td style="border: 1.5px solid black;">{inv['destination']}</td>
                    <td style="border: 1.5px solid black;">{inv['kolli']}</td>
                    <td style="border: 1.5px solid black;">Rp {int(inv['harga']):,}</td>
                    <td style="border: 1.5px solid black;">{inv['weight']} Kg</td>
                </tr>
                <tr style="font-weight: bold; background-color: #f2f2f2;">
                    <td colspan="6" style="border: 1.5px solid black; text-align: center; padding: 8px;">YANG HARUS DI BAYAR</td>
                    <td style="border: 1.5px solid black;">Rp {total_bayar:,}</td>
                </tr>
            </table>
            
            <div style="border: 1.5px solid black; margin-top: 8px; padding: 10px; font-size: 13px; font-style: italic; background-color: #eee;">
                <b>Terbilang :</b> {teks_terbilang}
            </div>

            <div style="margin-top: 30px; display: flex; justify-content: space-between; font-size: 13px;">
                <div style="flex: 1.5; line-height: 1.6;">
                    <b>TRANSFER TO :</b><br>
                    Bank Central Asia<br>
                    6720422334<br>
                    A/N ADITYA GAMA SAPUTRI<br>
                    <small><i>NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</i></small>
                </div>
                <div style="text-align: center; flex: 1;">
                    Sincerely,<br>
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width: 160px; margin: 10px 0;"><br>
                    <b><u>KELVINITO JAYADI</u></b><br>
                    DIREKTUR
                </div>
            </div>
        </div>
        """
        # INI ADALAH BAGIAN PENTING AGAR HTML TER-RENDER
        st.markdown(invoice_html, unsafe_allow_html=True)

# --- TAB 2: INPUT DATA BARU ---
with tab2:
    st.subheader("Input Transaksi Baru")
    with st.form("form_input", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_tgl = st.date_input("Tanggal Transaksi", datetime.now())
            f_cust = st.text_input("Nama Customer")
            f_desc = st.text_input("Deskripsi Barang")
        with col2:
            f_orig = st.text_input("Origin", value="SBY")
            f_dest = st.text_input("Destination")
            f_kolli = st.number_input("Kolli", min_value=1)
            f_harga = st.number_input("Harga Satuan", min_value=0)
            f_weight = st.number_input("Weight (Kg)", min_value=1)
            
        submit_btn = st.form_submit_button("💾 Simpan ke Database")
        
        if submit_btn:
            payload = {
                "date": f_tgl.strftime("%Y-%m-%d"),
                "customer": f_cust.upper(),
                "description": f_desc.upper(),
                "origin": f_orig.upper(),
                "destination": f_dest.upper(),
                "kolli": f_kolli,
                "harga": f_harga,
                "weight": f_weight,
                "total": f_harga * f_weight
            }
            try:
                res = requests.post(API_URL, data=json.dumps(payload))
                if res.status_code == 200:
                    st.success("Berhasil simpan! Silakan cek di tab 'Cetak Invoice'.")
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
