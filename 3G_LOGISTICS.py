import streamlit as st
import pandas as pd
import requests
import json
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS RESPONSIF & FIX GARIS
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container { padding: 10px; }
    
    /* Container untuk HP agar bisa scroll kiri-kanan */
    .invoice-wrapper {
        width: 100%;
        overflow-x: auto;
        background: #eeeeee;
        padding: 10px 0;
    }

    /* Area Invoice */
    #invoice-box {
        background: white;
        width: 790px; /* Standar A4 */
        margin: auto;
        padding: 30px;
        border: 2px solid black;
        box-sizing: border-box;
        color: black !important;
    }

    /* Hilangkan margin streamlit */
    .stTabs { margin-top: -20px; }
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

st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.error("Gagal ambil data!")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("Pilih Customer:", df['customer'].unique())
        row = df[df['customer'] == selected_cust].iloc[-1]
        tgl = str(row['date']).split('T')[0]
        total_harga = int(row['total'])
        teks_terbilang = terbilang(total_harga).title() + " Rupiah"

        # HTML INVOICE - SATU TABEL SOLID AGAR GARIS NYAMBUNG
        html_content = f"""
        <div class="invoice-wrapper">
        <div id="invoice-box">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%; display:block;">
            
            <div style="text-align:center; border-top:3px solid black; border-bottom:3px solid black; margin:15px 0; padding:10px; font-weight:bold; font-size:26px;">INVOICE</div>
            
            <table style="width:100%; font-weight:bold; margin-bottom:15px; font-size:16px;">
                <tr>
                    <td style="width:50%;">CUSTOMER : {row['customer']}</td>
                    <td style="width:50%; text-align:right;">DATE : {tgl}</td>
                </tr>
            </table>

            <table style="width:100%; border-collapse:collapse; border:2px solid black;">
                <thead>
                    <tr style="background-color:#316395; color:white; text-align:center;">
                        <th style="border:1px solid black; padding:10px;">Date of Load</th>
                        <th style="border:1px solid black;">Description</th>
                        <th style="border:1px solid black;">Origin</th>
                        <th style="border:1px solid black;">Dest</th>
                        <th style="border:1px solid black;">KOLLI</th>
                        <th style="border:1px solid black;">HARGA</th>
                        <th style="border:1px solid black;">WEIGHT</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="text-align:center;">
                        <td style="border:1px solid black; padding:20px;">{tgl}</td>
                        <td style="border:1px solid black;">{row['description']}</td>
                        <td style="border:1px solid black;">{row['origin']}</td>
                        <td style="border:1px solid black;">{row['destination']}</td>
                        <td style="border:1px solid black;">{row['kolli']}</td>
                        <td style="border:1px solid black;">Rp {int(row['harga']):,}</td>
                        <td style="border:1px solid black;">{row['weight']} Kg</td>
                    </tr>
                    <tr style="font-weight:bold; background-color:#f2f2f2;">
                        <td colspan="6" style="border:1px solid black; text-align:center; padding:12px;">YANG HARUS DI BAYAR</td>
                        <td style="border:1px solid black; text-align:center;">Rp {total_harga:,}</td>
                    </tr>
                    <tr>
                        <td colspan="7" style="border:1px solid black; padding:15px; font-style:italic; font-size:14px;">
                            <b>Terbilang :</b> {teks_terbilang}
                        </td>
                    </tr>
                </tbody>
            </table>

            <br><br>
            <table style="width:100%; font-size:14px; line-height:1.6;">
                <tr>
                    <td style="width:60%; vertical-align:top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia 6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br>
                        NB : Mohon konfirmasi ke Finance 082179799200
                    </td>
                    <td style="width:40%; text-align:center;">
                        Sincerely,<br>
                        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:160px; height:auto; margin:10px 0;">
                        <br><b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)

        # 3. FIX DOWNLOAD PDF (ANTI POTONG)
        st.write("---")
        components.html(f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
        <button onclick="generatePDF()" style="background-color:#4CAF50; color:white; padding:18px; border:none; border-radius:10px; cursor:pointer; width:100%; font-weight:bold; font-size:18px;">📥 DOWNLOAD PDF (A4 FULL)</button>
        <script>
        function generatePDF() {{
          const element = window.parent.document.getElementById('invoice-box');
          const opt = {{
            margin: [0.2, 0.2, 0.2, 0.2],
            filename: 'INV_{selected_cust}_{tgl}.pdf',
            image: {{ type: 'jpeg', quality: 0.98 }},
            html2canvas: {{ 
                scale: 2, 
                useCORS: true,
                width: 790,
                letterRendering: true
            }},
            jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
          }};
          html2pdf().set(opt).from(element).save();
        }}
        </script>""", height=100)

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
        
        if st.form_submit_button("SIMPAN DATA"):
            payload = {{"date":str(in_tgl),"customer":in_cust.upper(),"description":in_desc.upper(),"origin":in_orig.upper(),"destination":in_dest.upper(),"kolli":in_kol,"harga":in_hrg,"weight":in_kg,"total":in_hrg*in_kg}}
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success("Berhasil!")
                st.cache_data.clear()
            except:
                st.error("Gagal simpan.")
