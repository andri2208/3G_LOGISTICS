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

# CSS UNTUK TAMPILAN WEB RESPONSIF
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    iframe { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice (Responsif)", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.error("Gagal terhubung ke Database")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("Pilih Customer:", sorted(df['customer'].unique()))
        row = df[df['customer'] == selected_cust].iloc[-1]
        
        # LOGIKA TOTAL
        berat = extract_number(row['weight'])
        harga = extract_number(row['harga'])
        total_val = int(berat * harga) if berat > 0 else int(harga)
        
        tgl_raw = str(row['date']).split('T')[0]
        tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        teks_terbilang = terbilang(total_val).strip() + " Rupiah"

        # HTML DESAIN RESPONSIF A5
        html_desain = f"""
        <div id="invoice-box" style="background-color:white; padding:10px; color:black; font-family:Arial, sans-serif; width:100%; max-width:800px; margin:auto; border:1px solid #ddd; box-sizing:border-box;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%; height:auto;">
            
            <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold; font-size: clamp(16px, 4vw, 20px);">INVOICE</div>
            
            <div style="display:flex; justify-content:space-between; font-size: clamp(10px, 2.5vw, 13px); font-weight:bold; margin-bottom:10px;">
                <span>CUSTOMER : {row['customer']}</span>
                <span>DATE : {tgl_indo}</span>
            </div>
            
            <div style="overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; border:1px solid black; font-size: clamp(9px, 2vw, 11px); text-align:center;">
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
                        <td style="border:1px solid black; font-weight:bold;">Rp {total_val:,}</td>
                    </tr>
                    <tr style="font-weight:bold;">
                        <td colspan="6" style="border:1px solid black; text-align:right; padding:5px;">YANG HARUS DI BAYAR</td>
                        <td style="border:1px solid black; background-color:#eee;">Rp {total_val:,}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin-top:10px; font-size: clamp(10px, 2.2vw, 12px); border:1px solid black; padding:5px;"><b>Terbilang:</b> <i>{teks_terbilang}</i></div>
            
            <div style="margin-top:20px; display:flex; flex-wrap:wrap; justify-content:space-between; font-size: clamp(10px, 2.2vw, 11px);">
                <div style="flex:1; min-width:180px; margin-bottom:10px;">
                    <b>TRANSFER TO:</b><br>Bank Central Asia (BCA)<br>6720422334<br>A/N ADITYA GAMA SAPUTRI<br>
                    <small>Finance: 082179799200</small>
                </div>
                <div style="flex:1; text-align:center; min-width:150px;">
                    Sincerely,<br>
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:120px; height:auto; max-width:100%;"><br>
                    <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                </div>
            </div>
        </div>
        """
        st.markdown(html_desain, unsafe_allow_html=True)
        
        # TOMBOL DOWNLOAD PDF A5
        st.write("---")
        components.html(f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="downloadPDF()" style="width:100%; background-color:#28a745; color:white; padding:15px; border:none; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">📥 DOWNLOAD PDF (UKURAN A5)</button>
            <script>
            function downloadPDF() {{
                const element = window.parent.document.getElementById('invoice-box');
                const opt = {{
                    margin: 0.1,
                    filename: 'Invoice_{selected_cust}.pdf',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 3, useCORS: true }},
                    jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
            </script>
        """, height=100)

with tab2:
    st.subheader("➕ Tambah Data")
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        in_tgl = c1.date_input("Tanggal", datetime.now())
        in_cust = c1.text_input("Customer")
        in_desc = c1.text_input("Barang")
        in_orig = c2.text_input("Origin", value="SBY")
        in_dest = c2.text_input("Destination")
        in_kol = c2.text_input("Kolli")
        in_kg = c2.text_input("Weight (Kg/Unit)")
        in_hrg = c2.number_input("Harga Satuan", 0)
        
        if st.form_submit_button("SIMPAN"):
            w_val = extract_number(in_kg)
            t_val = int(w_val * in_hrg) if w_val > 0 else int(in_hrg)
            payload = {{
                "date": str(in_tgl), "customer": in_cust.upper(), "description": in_desc.upper(),
                "origin": in_orig.upper(), "destination": in_dest.upper(), "kolli": in_kol,
                "harga": in_hrg, "weight": in_kg, "total": t_val
            }}
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success(f"Tersimpan! Total Otomatis: Rp {t_val:,}")
                st.cache_data.clear()
            except:
                st.error("Gagal simpan.")
