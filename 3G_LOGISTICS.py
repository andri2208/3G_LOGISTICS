import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

# 2. CSS UNTUK TAMPILAN WEB (Auto-Zoom untuk HP)
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stTabs { margin-top: -15px; }
    
    /* Mencegah scroll horizontal pada container utama */
    .main .block-container { overflow-x: hidden; }

    /* Responsif khusus layar HP (lebar di bawah 600px) */
    @media only screen and (max-width: 600px) {
        #invoice-preview-container {
            zoom: 0.45; 
            -moz-transform: scale(0.45);
            -moz-transform-origin: 0 0;
            width: 100%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOGIN
def login():
    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)
    st.write("### 🔐 Akses Sistem 3G Logistics")
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Masuk"):
            if user == "admin3g" and pw == "gama2024":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Username atau Password Salah!")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
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

    # Baris Logout
    c_kosong, c_out = st.columns([0.8, 0.2])
    with c_out:
        if st.button("Logout 🚪", use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

    tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

    with tab1:
        data = get_data()
        if not data:
            st.warning("Memuat data...")
        else:
            df = pd.DataFrame(data)
            selected_cust = st.selectbox("Pilih Nama Customer:", df['customer'].unique())
            row = df[df['customer'] == selected_cust].iloc[-1]
            tgl = str(row['date']).split('T')[0]
            total_harga = int(row['total'])
            teks_terbilang = terbilang(total_harga).title() + " Rupiah"
            nama_file = f"INV_{selected_cust}_{tgl}.pdf"

            # --- DESAIN INVOICE PAS A4 ---
            html_content = f"""
<div id="invoice-preview-container">
<div id="invoice-box" style="background-color:white; padding:40px; border:1px solid #000; color:black; font-family:Arial, sans-serif; width:800px; margin:auto; box-sizing:border-box;">
    <center><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%; height:auto;"></center>
    <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:15px 0; padding:5px; font-weight:bold; font-size: 24px;">INVOICE</div>
    <table style="width:100%; font-weight:bold; font-size:16px; margin-bottom:15px;">
        <tr><td style="width:50%;">CUSTOMER : {row['customer']}</td><td style="width:50%; text-align:right;">DATE : {tgl}</td></tr>
    </table>
    <table style="width:100%; border-collapse:collapse; border:2px solid black; font-size: 13px; text-align:center;">
        <tr style="background-color:#316395; color:white;">
            <th style="border:1px solid black; padding:12px;">Date of Load</th><th style="border:1px solid black;">Description</th><th style="border:1px solid black;">Origin</th><th style="border:1px solid black;">Dest</th><th style="border:1px solid black;">KOLLI</th><th style="border:1px solid black;">HARGA</th><th style="border:1px solid black;">WEIGHT</th>
        </tr>
        <tr>
            <td style="border:1px solid black; padding:20px;">{tgl}</td><td style="border:1px solid black;">{row['description']}</td><td style="border:1px solid black;">{row['origin']}</td><td style="border:1px solid black;">{row['destination']}</td><td style="border:1px solid black;">{row['kolli']}</td><td style="border:1px solid black;">Rp {int(row['harga']):,}</td><td style="border:1px solid black;">{row['weight']} Kg</td>
        </tr>
        <tr style="font-weight:bold; background-color:#f2f2f2;">
            <td colspan="6" style="border:1px solid black; text-align:center; padding:12px;">YANG HARUS DI BAYAR</td><td style="border:1px solid black;">Rp {total_harga:,}</td>
        </tr>
    </table>
    <div style="border:2px solid black; border-top:none; padding:12px; font-size: 14px; font-style:italic;">
        <b>Terbilang :</b> {teks_terbilang}
    </div>
    <br><br>
    <table style="width:100%; font-size:13px; line-height:1.6;">
        <tr>
            <td style="width:60%; vertical-align:top;">
                <b style="font-size:14px;">TRANSFER TO :</b><br>
                Bank Central Asia 6720422334<br>
                A/N ADITYA GAMA SAPUTRI<br>
                NB : Jika sudah transfer mohon konfirmasi ke<br>
                Finance 082179799200
            </td>
            <td style="width:40%; text-align:center; vertical-align:top;">
                Sincerely,<br><img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:160px; height:auto; margin:10px 0;"><br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
            </td>
        </tr>
    </table>
</div>
</div>
"""
            st.markdown(html_content, unsafe_allow_html=True)
            st.write("---")

            # 4. SCRIPT DOWNLOAD
            components.html(f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<button onclick="generatePDF()" style="background-color:#4CAF50; color:white; padding:18px; border:none; border-radius:10px; cursor:pointer; width:100%; font-weight:bold; font-size:18px;">📥 SIMPAN SEBAGAI PDF</button>
<script>
function generatePDF() {{
  const element = window.parent.document.getElementById('invoice-box');
  const opt = {{
    margin: [0.3, 0.3, 0.3, 0.3],
    filename: '{nama_file}',
    image: {{ type: 'jpeg', quality: 0.98 }},
    html2canvas: {{ scale: 2, useCORS: true, width: 800 }},
    jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
  }};
  html2pdf().set(opt).from(element).save();
}}
</script>""", height=100)

    with tab2:
        st.subheader("➕ Input Data Pengiriman")
        with st.form("form_entry", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_tgl = c1.date_input("Tanggal")
            f_cust = c1.text_input("Customer")
            f_desc = c1.text_input("Barang")
            f_orig = c2.text_input("Origin", value="SBY")
            f_dest = c2.text_input("Destination")
            f_kol = c2.number_input("Kolli", 0)
            f_kg = c2.number_input("Weight (Kg)", 1)
            f_hrg = c2.number_input("Harga Satuan", 0)
            
            if st.form_submit_button("🚀 SIMPAN DATA"):
                payload = {
                    "date": str(f_tgl), "customer": f_cust.upper(), "description": f_desc.upper(),
                    "origin": f_orig.upper(), "destination": f_dest.upper(), "kolli": f_kol,
                    "harga": f_hrg, "weight": f_kg, "total": f_hrg * f_kg
                }
                try:
                    requests.post(API_URL, data=json.dumps(payload))
                    st.success("Berhasil Disimpan!")
                    st.cache_data.clear()
                except:
                    st.error("Gagal simpan.")
