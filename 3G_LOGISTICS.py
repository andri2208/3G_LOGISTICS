import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

def terbilang(n):
    bil = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    if n < 12: return bil[int(n)]
    elif n < 20: return terbilang(n - 10) + " belas"
    elif n < 100: return terbilang(n // 10) + " puluh " + terbilang(n % 10)
    elif n < 200: return " seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " ratus " + terbilang(n % 100)
    elif n < 2000: return " seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    return ""

@st.cache_data(ttl=5)
def get_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except: return []

# Header Utama Web
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.error("Data tidak tersedia")
    else:
        df = pd.DataFrame(data)
        cust_pilih = st.selectbox("Pilih Customer:", df['customer'].unique())
        row = df[df['customer'] == cust_pilih].iloc[-1]
        tgl = str(row['date']).split('T')[0]
        total_harga = int(row['total'])
        teks_terbilang = terbilang(total_harga).title() + " Rupiah"
        nama_file = f"INV_{cust_pilih}_{tgl}.pdf"

        # HTML Tanpa Indentasi Spasi di Awal
        html_desain = f"""<div id="print-area" style="background-color:white;padding:15px;border:1px solid black;color:black;font-family:Arial;width:100%;max-width:750px;margin:auto;box-sizing:border-box;">
<center><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;"></center>
<div style="text-align:center;border-top:2px solid black;border-bottom:2px solid black;margin:10px 0;padding:5px;font-weight:bold;font-size:20px;">INVOICE</div>
<div style="display:flex;justify-content:space-between;font-size:14px;margin-bottom:10px;"><b>CUSTOMER: {row['customer']}</b><b>DATE: {tgl}</b></div>
<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;border:1px solid black;font-size:11px;text-align:center;">
<tr style="background-color:#316395;color:white;"><th style="border:1px solid black;padding:5px;">Date of Load</th><th style="border:1px solid black;">Description</th><th style="border:1px solid black;">Origin</th><th style="border:1px solid black;">Dest</th><th style="border:1px solid black;">KOLLI</th><th style="border:1px solid black;">HARGA</th><th style="border:1px solid black;">WEIGHT</th></tr>
<tr><td style="border:1px solid black;padding:8px;">{tgl}</td><td style="border:1px solid black;">{row['description']}</td><td style="border:1px solid black;">{row['origin']}</td><td style="border:1px solid black;">{row['destination']}</td><td style="border:1px solid black;">{row['kolli']}</td><td style="border:1px solid black;">Rp {int(row['harga']):,}</td><td style="border:1px solid black;">{row['weight']} Kg</td></tr>
<tr style="font-weight:bold;background-color:#f2f2f2;"><td colspan="6" style="border:1px solid black;text-align:center;padding:5px;">YANG HARUS DI BAYAR</td><td style="border:1px solid black;">Rp {total_harga:,}</td></tr></table></div>
<div style="border:1px solid black;margin-top:5px;padding:8px;font-size:12px;font-style:italic;"><b>Terbilang:</b> {teks_terbilang}</div>
<div style="margin-top:20px;display:flex;justify-content:space-between;font-size:12px;">
<div style="width:50%;"><b>TRANSFER TO:</b><br>Bank Central Asia<br>6720422334<br>A/N ADITYA GAMA SAPUTRI</div>
<div style="text-align:center;width:50%;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:120px;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</div>
</div></div>"""

        # Tampilkan Invoice
        st.markdown(html_desain, unsafe_allow_html=True)

        # Tombol Download
        st.write("---")
        components.html(f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<button onclick="savePDF()" style="background-color:#4CAF50;color:white;padding:15px;border:none;border-radius:8px;cursor:pointer;width:100%;font-weight:bold;">📥 SIMPAN KE PDF</button>
<script>
function savePDF() {{
  const element = window.parent.document.getElementById('print-area');
  const opt = {{ margin:0.2, filename:'{nama_file}', image:{{type:'jpeg', quality:0.98}}, html2canvas:{{scale:3, useCORS:true}}, jsPDF:{{unit:'in', format:'a4', orientation:'portrait'}} }};
  html2pdf().set(opt).from(element).save();
}}
</script>""", height=80)

with tab2:
    with st.form("input_transaksi", clear_on_submit=True):
        col1, col2 = st.columns(2)
        f_tgl = col1.date_input("Tanggal")
        f_cust = col1.text_input("Customer")
        f_desc = col1.text_input("Barang")
        f_ori = col2.text_input("Origin", value="SBY")
        f_dest = col2.text_input("Destination")
        f_kol = col2.number_input("Kolli", 0)
        f_kg = col2.number_input("Weight (Kg)", 1)
        f_hrg = col2.number_input("Harga", 0)
        if st.form_submit_button("SIMPAN DATA"):
            pld = {"date":str(f_tgl),"customer":f_cust.upper(),"description":f_desc.upper(),"origin":f_ori.upper(),"destination":f_dest.upper(),"kolli":f_kol,"harga":f_hrg,"weight":f_kg,"total":f_hrg*f_kg}
            requests.post(API_URL, data=json.dumps(pld))
            st.success("Tersimpan!")
            st.cache_data.clear()
