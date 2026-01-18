import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# 1. KONFIGURASI
st.set_page_config(page_title="3G Logistics", layout="wide")

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

# 2. DATA FETCHING
@st.cache_data(ttl=10)
def get_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except:
        return []

# 3. TAMPILAN
st.title("PT. GAMA GEMAH GEMILANG")

t1, t2 = st.tabs(["Cetak Invoice", "Tambah Data"])

with t1:
    data = get_data()
    if not data:
        st.error("Database Kosong atau Error")
    else:
        df = pd.DataFrame(data)
        st.sidebar.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png")
        cust = st.sidebar.selectbox("Pilih Customer", df['customer'].unique())
        
        # Ambil data terbaru customer
        row = df[df['customer'] == cust].iloc[-1]
        tgl = str(row['date']).split('T')[0]
        total = int(row['total'])
        kata = terbilang(total).title() + " Rupiah"

        # HTML TANPA INDENTASI (Kunci perbaikan)
        html_code = f"""
<div style="background-color:white; padding:20px; border:2px solid black; color:black; font-family:Arial;">
<center><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" width="100%"></center>
<div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold; font-size:20px;">INVOICE</div>
<table style="width:100%; font-size:14px; margin-bottom:10px;">
<tr><td><b>CUSTOMER : {row['customer']}</b></td><td style="text-align:right;"><b>DATE : {tgl}</b></td></tr>
</table>
<table style="width:100%; border-collapse:collapse; border:1px solid black; font-size:12px; text-align:center;">
<tr style="background-color:#316395; color:white;">
<th style="border:1px solid black; padding:8px;">Date of Load</th>
<th style="border:1px solid black;">Product Description</th>
<th style="border:1px solid black;">Origin</th>
<th style="border:1px solid black;">Destination</th>
<th style="border:1px solid black;">KOLLI</th>
<th style="border:1px solid black;">HARGA</th>
<th style="border:1px solid black;">WEIGHT</th>
</tr>
<tr>
<td style="border:1px solid black; padding:10px;">{tgl}</td>
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
<div style="border:1px solid black; margin-top:5px; padding:8px; font-size:13px; font-style:italic;"><b>Terbilang :</b> {kata}</div>
<div style="margin-top:20px; display:flex; justify-content:space-between; font-size:12px;">
<div style="width:50%;"><b>TRANSFER TO :</b><br>Bank Central Asia<br>6720422334<br>A/N ADITYA GAMA SAPUTRI<br><small>NB: Konfirmasi Finance 082179799200</small></div>
<div style="text-align:center; width:50%;">Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" width="150px"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR</div>
</div>
</div>
"""
        # Eksekusi Render
        st.markdown(html_code, unsafe_allow_html=True)
        st.button("Print (Ctrl+P)")

with t2:
    with st.form("f1", clear_on_submit=True):
        c1, c2 = st.columns(2)
        d_tgl = c1.date_input("Tanggal")
        d_cust = c1.text_input("Customer")
        d_item = c1.text_input("Barang")
        d_ori = c2.text_input("Origin")
        d_dest = c2.text_input("Dest")
        d_kg = c2.number_input("Berat", 1)
        d_hrg = c2.number_input("Harga", 0)
        if st.form_submit_button("Simpan"):
            payload = {"date":str(d_tgl), "customer":d_cust.upper(), "description":d_item.upper(), "origin":d_ori.upper(), "destination":d_dest.upper(), "kolli":0, "harga":d_hrg, "weight":d_kg, "total":d_hrg*d_kg}
            requests.post(API_URL, data=json.dumps(payload))
            st.success("Data Tersimpan!")
            st.cache_data.clear()
