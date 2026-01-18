import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")
# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

# --- TAMBAHKAN CSS INI UNTUK MENARIK TAMPILAN KE ATAS ---
st.markdown("""
    <style>
    /* Menghilangkan jarak atas pada aplikasi */
    .block-container {
        padding-top: 40px;
        padding-bottom: 0rem;
        margin-top: -20px;
    }
    /* Menghilangkan ruang kosong di atas tabs */
    .stTabs {
        margin-top: -20px;
    }
    /* Mengatur jarak header agar tidak terlalu besar */
    [data-testid="stImage"] {
        margin-top: -30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEM LOGIN SEDERHANA ---
def login():
    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)
    st.subheader("🔐 Login System")
    
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_button("Masuk")
        
        if submit:
            # GANTI USERNAME & PASSWORD DI SINI
            if user == "admin" and pw == "2026":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Username atau Password Salah!")

# Cek status login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    # --- JIKA SUDAH LOGIN, TAMPILKAN APLIKASI ---
    
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

    # Tombol Logout di pojok kanan atas
    col_header, col_logout = st.columns([0.8, 0.2])
    with col_logout:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

    tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

    with tab1:
        data = get_data()
        if not data:
            st.error("Database Kosong")
        else:
            df = pd.DataFrame(data)
            selected_cust = st.selectbox("Pilih Customer:", df['customer'].unique())
            row = df[df['customer'] == selected_cust].iloc[-1]
            tgl = str(row['date']).split('T')[0]
            total_harga = int(row['total'])
            teks_terbilang = terbilang(total_harga).title() + " Rupiah"
            nama_file = f"INV_{selected_cust}_{tgl}.pdf"

            # HTML INVOICE
            html_desain = f"""<div id="invoice-box" style="background-color:white;padding:15px;border:1px solid black;color:black;font-family:Arial, sans-serif;width:100%;max-width:750px;margin:auto;box-sizing:border-box;">
<center><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%; height:auto;"></center>
<div style="text-align:center;border-top:2px solid black;border-bottom:2px solid black;margin:10px 0;padding:5px;font-weight:bold;font-size: 20px;">INVOICE</div>
<div style="display:flex;justify-content:space-between;font-size: 14px;margin-bottom:10px;font-weight:bold;"><span>CUSTOMER : {row['customer']}</span><span>DATE : {tgl}</span></div>
<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;border:1px solid black;font-size: 11px;text-align:center;">
<tr style="background-color:#316395;color:white;"><th style="border:1px solid black;padding:5px;">Date of Load</th><th style="border:1px solid black;">Description</th><th style="border:1px solid black;">Origin</th><th style="border:1px solid black;">Dest</th><th style="border:1px solid black;">KOLLI</th><th style="border:1px solid black;">HARGA</th><th style="border:1px solid black;">WEIGHT</th></tr>
<tr><td style="border:1px solid black;padding:8px;">{tgl}</td><td style="border:1px solid black;">{row['description']}</td><td style="border:1px solid black;">{row['origin']}</td><td style="border:1px solid black;">{row['destination']}</td><td style="border:1px solid black;">{row['kolli']}</td><td style="border:1px solid black;">Rp {int(row['harga']):,}</td><td style="border:1px solid black;">{row['weight']} Kg</td></tr>
<tr style="font-weight:bold;background-color:#f2f2f2;"><td colspan="6" style="border:1px solid black;text-align:center;padding:5px;">YANG HARUS DI BAYAR</td><td style="border:1px solid black;">Rp {total_harga:,}</td></tr></table></div>
<div style="border:1px solid black;margin-top:5px;padding:8px;font-size: 12px;font-style:italic;"><b>Terbilang :</b> {teks_terbilang}</div>
<div style="margin-top:20px;display:flex;flex-wrap:wrap;justify-content:space-between;font-size: 12px;">
<div style="flex:1;min-width:200px;margin-bottom:15px;">
<b>TRANSFER TO :</b><br>Bank Central Asia<br>6720422334<br>A/N ADITYA GAMA SAPUTRI<br><small>NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</small>
</div>
<div style="flex:1;text-align:center;min-width:150px;">
Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:130px; height:auto; margin:5px 0;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
</div></div></div>"""

            st.markdown(html_desain, unsafe_allow_html=True)

            st.write("---")
            components.html(f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<button onclick="downloadPDF()" style="background-color:#4CAF50;color:white;padding:15px;border:none;border-radius:8px;cursor:pointer;width:100%;font-weight:bold;font-size:16px;">📥 DOWNLOAD INVOICE (PDF)</button>
<script>
function downloadPDF() {{
  const element = window.parent.document.getElementById('invoice-box');
  const opt = {{
    margin: [0.2, 0.2, 0.2, 0.2],
    filename: '{nama_file}',
    image: {{ type: 'jpeg', quality: 0.98 }},
    html2canvas: {{ scale: 3, useCORS: true }},
    jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
  }};
  html2pdf().set(opt).from(element).save();
}}
</script>""", height=80)

    with tab2:
        st.subheader("➕ Input Data Baru")
        with st.form("form_entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            in_tgl = c1.date_input("Tanggal")
            in_cust = c1.text_input("Customer")
            in_desc = c1.text_input("Barang")
            in_orig = c2.text_input("Origin", value="SBY")
            in_dest = c2.text_input("Destination")
            in_kol = c2.number_input("Kolli", 0)
            in_kg = c2.number_input("Weight (Kg)", 1)
            in_hrg = c2.number_input("Harga Satuan", 0)
            
            if st.form_submit_button("SIMPAN KE DATABASE"):
                payload = {{"date":str(in_tgl),"customer":in_cust.upper(),"description":in_desc.upper(),"origin":in_orig.upper(),"destination":in_dest.upper(),"kolli":in_kol,"harga":in_hrg,"weight":in_kg,"total":in_hrg*in_kg}}
                try:
                    requests.post(API_URL, data=json.dumps(payload))
                    st.success("Data Berhasil Disimpan!")
                    st.cache_data.clear()
                except:
                    st.error("Gagal menyimpan data.")







