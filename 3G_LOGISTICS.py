import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS untuk menghilangkan padding berlebih di mobile
st.markdown("""
    <style>
    .main > div { padding-top: 2rem; }
    iframe { max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

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

# HEADER WEB
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

t1, t2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

with t1:
    data = get_data()
    if not data:
        st.error("Database Kosong")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("Pilih Customer:", df['customer'].unique())
        row = df[df['customer'] == selected_cust].iloc[-1]
        tgl = str(row['date']).split('T')[0]
        total = int(row['total'])
        kata = terbilang(total).title() + " Rupiah"
        filename = f"INV_{selected_cust}_{tgl}.pdf"

        # Tampilan Invoice Responsive
        invoice_html = f"""
<div id="invoice-area" style="background-color:white; padding:10px; border:1px solid black; color:black; font-family:Arial, sans-serif; width:100%; max-width:750px; margin:auto; box-sizing:border-box;">
    <center><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%; height:auto;"></center>
    
    <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold; font-size: clamp(14px, 4vw, 18px);">INVOICE</div>
    
    <div style="display:flex; justify-content:space-between; font-size: clamp(10px, 3vw, 13px); margin-bottom:10px; font-weight:bold;">
        <span>CUSTOMER : {row['customer']}</span>
        <span>DATE : {tgl}</span>
    </div>

    <div style="overflow-x:auto; width:100%; -webkit-overflow-scrolling: touch;">
        <table style="width:100%; border-collapse:collapse; border:1px solid black; font-size: clamp(9px, 2.5vw, 11px); text-align:center; min-width: 500px;">
            <tr style="background-color:#316395; color:white;">
                <th style="border:1px solid black; padding:5px;">Date of Load</th>
                <th style="border:1px solid black;">Description</th>
                <th style="border:1px solid black;">Origin</th>
                <th style="border:1px solid black;">Dest</th>
                <th style="border:1px solid black;">KOLLI</th>
                <th style="border:1px solid black;">HARGA</th>
                <th style="border:1px solid black;">WEIGHT</th>
            </tr>
            <tr>
                <td style="border:1px solid black; padding:8px;">{tgl}</td>
                <td style="border:1px solid black;">{row['description']}</td>
                <td style="border:1px solid black;">{row['origin']}</td>
                <td style="border:1px solid black;">{row['destination']}</td>
                <td style="border:1px solid black;">{row['kolli']}</td>
                <td style="border:1px solid black;">Rp {int(row['harga']):,}</td>
                <td style="border:1px solid black;">{row['weight']} Kg</td>
            </tr>
            <tr style="font-weight:bold; background-color:#f2f2f2;">
                <td colspan="6" style="border:1px solid black; text-align:center; padding:5px;">YANG HARUS DI BAYAR</td>
                <td style="border:1px solid black;">Rp {total:,}</td>
            </tr>
        </table>
    </div>

    <div style="border:1px solid black; margin-top:5px; padding:8px; font-size: clamp(10px, 3vw, 12px); font-style: italic; background-color: #fafafa;">
        <b>Terbilang :</b> {kata}
    </div>

    <div style="margin-top:20px; display:flex; flex-wrap:wrap; justify-content:space-between; font-size: clamp(10px, 3vw, 12px);">
        <div style="flex: 1; min-width: 180px; margin-bottom: 10px;">
            <b>TRANSFER TO :</b><br>Bank Central Asia<br>6720422334<br>A/N ADITYA GAMA SAPUTRI<br><small>NB: Konfirmasi Finance 082179799200</small>
        </div>
        <div style="flex: 1; text-align: center; min-width: 150px;">
            Sincerely,<br>
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:120px; height:auto;"><br>
            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
        </div>
    </div>
</div>
"""
        st.markdown(invoice_html, unsafe_allow_html=True)
        
        st.write("")
        components.html(f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <script>
            function downloadPDF() {{
                const element = window.parent.document.getElementById('invoice-area');
                const opt = {{
                    margin: [0.1, 0.1, 0.1, 0.1],
                    filename: '{filename}',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 3, useCORS: true, letterRendering: true }},
                    jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
            </script>
            <button onclick="downloadPDF()" style="background-color: #4CAF50; color: white; padding: 15px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; font-weight: bold; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                📥 DOWNLOAD INVOICE (PDF)
            </button>
        """, height=100)

with t2:
    st.subheader("📝 Input Transaksi Baru")
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        d_tgl = c1.date_input("Tanggal")
        d_cust = c1.text_input("Customer")
        d_item = c1.text_input("Barang")
        d_ori = c2.text_input("Origin", value="SBY")
        d_dest = c2.text_input("Destination")
        d_kol = c2.number_input("Kolli", 0)
        d_kg = c2.number_input("Weight (Kg)", 1)
        d_hrg = c2.number_input("Harga", 0)
        
        if st.form_submit_button("🚀 SIMPAN DATA"):
            payload = {
                "date": str(d_tgl), "customer": d_cust.upper(), "description": d_item.upper(),
                "origin": d_ori.upper(), "destination": d_dest.upper(), "kolli": d_kol,
                "harga": d_hrg, "weight": d_kg, "total": d_hrg * d_kg
            }
            requests.post(API_URL, data=json.dumps(payload))
            st.success("✅ Tersimpan!")
            st.cache_data.clear()
