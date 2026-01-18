import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered")

API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# FUNGSI EKSTRAK ANGKA (Mengambil angka saja dari teks seperti "290 Kg" atau "Rp 8.500")
def extract_number(value):
    if pd.isna(value) or value == "": return 0
    # Mencari angka (termasuk desimal jika ada)
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
    if match:
        return float(match[0])
    return 0

def terbilang(n):
    bil = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bil[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return " Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return " Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return ""

@st.cache_data(ttl=2)
def get_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except: return []

# HEADER
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.error("Gagal terhubung ke Database")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("Pilih Customer:", sorted(df['customer'].unique()))
        row = df[df['customer'] == selected_cust].iloc[-1]
        
        # --- LOGIKA TOTAL OTOMATIS ---
        berat = extract_number(row['weight'])
        harga = extract_number(row['harga'])
        
        # Jika berat 0 (mungkin borongan), pakai harga saja. Jika ada berat, kalikan.
        total_otomatis = int(berat * harga) if berat > 0 else int(harga)
        
        tgl_raw = str(row['date']).split('T')[0]
        tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        teks_terbilang = terbilang(total_otomatis).strip() + " Rupiah"

        # TAMPILAN HTML
        html_desain = f"""
        <div id="invoice-box" style="background-color:white; padding:20px; color:black; font-family:Arial; border:1px solid #ccc;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
            <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold;">INVOICE</div>
            <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:bold; margin-bottom:10px;">
                <span>CUSTOMER : {row['customer']}</span>
                <span>DATE : {tgl_indo}</span>
            </div>
            <table style="width:100%; border-collapse:collapse; border:1px solid black; font-size:11px; text-align:center;">
                <tr style="background-color:#f2f2f2;">
                    <th style="border:1px solid black; padding:5px;">Description</th>
                    <th style="border:1px solid black;">Origin</th>
                    <th style="border:1px solid black;">Dest</th>
                    <th style="border:1px solid black;">KOLLI</th>
                    <th style="border:1px solid black;">HARGA</th>
                    <th style="border:1px solid black;">WEIGHT</th>
                    <th style="border:1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:10px;">{row['description']}</td>
                    <td style="border:1px solid black;">{row['origin']}</td>
                    <td style="border:1px solid black;">{row['destination']}</td>
                    <td style="border:1px solid black;">{row['kolli']}</td>
                    <td style="border:1px solid black;">Rp {int(harga):,}</td>
                    <td style="border:1px solid black;">{row['weight']}</td>
                    <td style="border:1px solid black; font-weight:bold;">Rp {total_otomatis:,}</td>
                </tr>
                <tr style="font-weight:bold;">
                    <td colspan="6" style="border:1px solid black; text-align:right; padding:5px;">TOTAL YANG HARUS DIBAYAR</td>
                    <td style="border:1px solid black; background-color:#eee;">Rp {total_otomatis:,}</td>
                </tr>
            </table>
            <div style="margin-top:10px; font-size:11px;"><b>Terbilang:</b> <i>{teks_terbilang}</i></div>
            <div style="margin-top:20px; display:flex; justify-content:space-between; font-size:11px;">
                <div><b>TRANSFER TO:</b><br>BCA: 6720422334<br>A/N ADITYA GAMA SAPUTRI</div>
                <div style="text-align:center;">
                    Sincerely,<br>
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:120px;"><br>
                    <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                </div>
            </div>
        </div>
        """
        st.markdown(html_desain, unsafe_allow_html=True)
        
        # Tombol Download
        components.html(f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="download()" style="width:100%; background-color:#28a745; color:white; padding:12px; border:none; border-radius:5px; cursor:pointer; font-weight:bold; margin-top:10px;">📥 DOWNLOAD PDF</button>
            <script>
            function download() {{
                const element = window.parent.document.getElementById('invoice-box');
                html2pdf().set({{ margin: 0.2, filename: 'Invoice_{selected_cust}.pdf', html2canvas: {{ scale: 3, useCORS: true }}, jsPDF: {{ format: 'a4' }} }}).from(element).save();
            }}
            </script>
        """, height=70)

with tab2:
    st.subheader("➕ Tambah Data Ke Database")
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        in_tgl = c1.date_input("Tanggal")
        in_cust = c1.text_input("Customer")
        in_desc = c1.text_input("Deskripsi Barang")
        in_orig = c2.text_input("Origin", value="SBY")
        in_dest = c2.text_input("Destination")
        in_kol = c2.text_input("Kolli")
        in_kg = c2.text_input("Weight (Contoh: 290)")
        in_hrg = c2.number_input("Harga Satuan", 0)
        
        if st.form_submit_button("SIMPAN DATA"):
            # Perhitungan otomatis sebelum kirim ke database
            w_val = extract_number(in_kg)
            t_val = int(w_val * in_hrg) if w_val > 0 else int(in_hrg)
            
            payload = {
                "date": str(in_tgl), "customer": in_cust.upper(), "description": in_desc.upper(),
                "origin": in_orig.upper(), "destination": in_dest.upper(), "kolli": in_kol,
                "harga": in_hrg, "weight": in_kg, "total": t_val
            }
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success(f"Data Berhasil Disimpan! Total Otomatis: Rp {t_val:,}")
                st.cache_data.clear()
            except:
                st.error("Gagal Simpan.")
