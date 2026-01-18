import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', ''))
    if match: return float(match[0])
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

# HEADER DASHBOARD
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.warning("Menghubungkan ke Database...")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("Pilih Customer:", sorted(df['customer'].unique()))
        row = df[df['customer'] == selected_cust].iloc[-1]
        
        # HITUNG TOTAL
        berat = extract_number(row['weight'])
        harga = extract_number(row['harga'])
        total_val = int(berat * harga) if berat > 0 else int(harga)
        
        tgl_raw = str(row['date']).split('T')[0]
        tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        teks_terbilang = terbilang(total_val).strip() + " Rupiah"

        # HTML DESIGN (DIBUAT LEBIH SEDERHANA AGAR TIDAK ERROR)
        html_content = f"""
        <div id="print-area" style="background:white; padding:10px; font-family:Arial; width:100%; max-width:750px; margin:auto; border:1px solid #ccc;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
            <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold; font-size:18px;">INVOICE</div>
            
            <table style="width:100%; font-size:12px; margin-bottom:10px; font-weight:bold;">
                <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
            </table>

            <table style="width:100%; border-collapse:collapse; border:1px solid black; font-size:11px; text-align:center;">
                <tr style="background:#eee;">
                    <th style="border:1px solid black; padding:5px;">Description</th>
                    <th style="border:1px solid black;">Origin</th>
                    <th style="border:1px solid black;">Dest</th>
                    <th style="border:1px solid black;">KOLLI</th>
                    <th style="border:1px solid black;">HARGA</th>
                    <th style="border:1px solid black;">WEIGHT</th>
                    <th style="border:1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:8px;">{row['description']}</td>
                    <td style="border:1px solid black;">{row['origin']}</td>
                    <td style="border:1px solid black;">{row['destination']}</td>
                    <td style="border:1px solid black;">{row['kolli']}</td>
                    <td style="border:1px solid black;">Rp {int(harga):,}</td>
                    <td style="border:1px solid black;">{row['weight']}</td>
                    <td style="border:1px solid black; font-weight:bold;">Rp {total_val:,}</td>
                </tr>
                <tr style="font-weight:bold; background:#f9f9f9;">
                    <td colspan="6" style="border:1px solid black; text-align:right; padding:5px;">YANG HARUS DI BAYAR</td>
                    <td style="border:1px solid black;">Rp {total_val:,}</td>
                </tr>
            </table>
            
            <div style="margin-top:10px; font-size:11px; border:1px solid black; padding:5px;"><b>Terbilang:</b> {teks_terbilang}</div>
            
            <table style="width:100%; margin-top:20px; font-size:11px;">
                <tr>
                    <td style="width:60%;"><b>TRANSFER TO:</b><br>Bank Central Asia (BCA)<br>6720422334<br>A/N ADITYA GAMA SAPUTRI</td>
                    <td style="text-align:center;">
                        Sincerely,<br>
                        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:120px;"><br>
                        <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # Tampilkan di Streamlit
        st.markdown(html_content, unsafe_allow_html=True)

        # Tombol Download (Menggunakan IFrame agar tidak bentrok dengan layout)
        st.write("---")
        components.html(f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="savePDF()" style="width:100%; background:#28a745; color:white; padding:15px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📥 DOWNLOAD INVOICE (UKURAN A5)</button>
            <script>
            function savePDF() {{
                const element = window.parent.document.getElementById('print-area');
                const opt = {{
                    margin: 0.1,
                    filename: 'Inv_{selected_cust}.pdf',
                    html2canvas: {{ scale: 3, useCORS: true }},
                    jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
            </script>
        """, height=80)

with tab2:
    st.subheader("➕ Tambah Data")
    with st.form("f_input", clear_on_submit=True):
        c1, c2 = st.columns(2)
        i_tgl = c1.date_input("Tanggal", datetime.now())
        i_cust = c1.text_input("Customer")
        i_desc = c1.text_input("Barang")
        i_orig = c2.text_input("Origin", value="SBY")
        i_dest = c2.text_input("Destination")
        i_kol = c2.text_input("Kolli")
        i_kg = c2.text_input("Weight")
        i_hrg = c2.number_input("Harga Satuan", 0)
        
        if st.form_submit_button("SIMPAN DATA"):
            w_num = extract_number(i_kg)
            t_num = int(w_num * i_hrg) if w_num > 0 else int(i_hrg)
            payload = {{
                "date": str(i_tgl), "customer": i_cust.upper(), "description": i_desc.upper(),
                "origin": i_orig.upper(), "destination": i_dest.upper(), "kolli": i_kol,
                "harga": i_hrg, "weight": i_kg, "total": t_num
            }}
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success(f"Data Berhasil Disimpan! Total: Rp {{t_num:,}}")
                st.cache_data.clear()
            except:
                st.error("Gagal simpan.")
