import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

# 2. CSS UNTUK TAMPILAN WEB (Full Responsif)
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container { padding: 1rem; }
    
    /* Container Pratinjau */
    .invoice-container {
        width: 100%;
        max-width: 800px;
        margin: auto;
        background: white;
        color: black;
        border: 2px solid black;
        font-family: Arial, sans-serif;
    }

    /* Responsif HP: Tabel bisa di-geser kalau layar terlalu kecil */
    .table-wrapper {
        width: 100%;
        overflow-x: auto;
    }

    @media only screen and (max-width: 600px) {
        .invoice-box { padding: 15px !important; }
        .inv-title { font-size: 18px !important; }
        .inv-text { font-size: 11px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOGIN
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == "admin3g" and p == "gama2024":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Salah password gan")
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
        try: return requests.get(API_URL).json()
        except: return []

    tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

    with tab1:
        data = get_data()
        if data:
            df = pd.DataFrame(data)
            cust = st.selectbox("Pilih Customer:", df['customer'].unique())
            row = df[df['customer'] == cust].iloc[-1]
            tgl = str(row['date']).split('T')[0]
            total = int(row['total'])
            teks = terbilang(total).title() + " Rupiah"

            # --- DESAIN INVOICE GARIS MENYAMBUNG (TABEL TUNGGAL) ---
            html_invoice = f"""
            <div id="invoice-download-area" style="background:white; padding:30px; width:800px; margin:auto; color:black;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
                <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold; font-size:22px;">INVOICE</div>
                
                <table style="width:100%; font-weight:bold; margin-bottom:10px;">
                    <tr><td>CUSTOMER : {row['customer']}</td><td style="text-align:right;">DATE : {tgl}</td></tr>
                </table>

                <table style="width:100%; border-collapse:collapse; border:2px solid black;">
                    <thead>
                        <tr style="background:#316395; color:white;">
                            <th style="border:1px solid black; padding:8px;">Date of Load</th>
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
                            <td style="border:1px solid black; padding:15px;">{tgl}</td>
                            <td style="border:1px solid black;">{row['description']}</td>
                            <td style="border:1px solid black;">{row['origin']}</td>
                            <td style="border:1px solid black;">{row['destination']}</td>
                            <td style="border:1px solid black;">{row['kolli']}</td>
                            <td style="border:1px solid black;">Rp {int(row['harga']):,}</td>
                            <td style="border:1px solid black;">{row['weight']} Kg</td>
                        </tr>
                        <tr style="font-weight:bold; background:#f2f2f2;">
                            <td colspan="6" style="border:1px solid black; text-align:center; padding:10px;">YANG HARUS DI BAYAR</td>
                            <td style="border:1px solid black; text-align:center;">Rp {total:,}</td>
                        </tr>
                        <tr>
                            <td colspan="7" style="border:2px solid black; padding:10px; font-style:italic;">
                                <b>Terbilang :</b> {teks}
                            </td>
                        </tr>
                    </tbody>
                </table>

                <br><br>
                <table style="width:100%; line-height:1.5;">
                    <tr>
                        <td style="width:60%; vertical-align:top;">
                            <b>TRANSFER TO :</b><br>
                            Bank Central Asia 6720422334<br>
                            A/N ADITYA GAMA SAPUTRI<br>
                            NB : Jika sudah transfer mohon konfirmasi ke<br>
                            Finance 082179799200
                        </td>
                        <td style="width:40%; text-align:center;">
                            Sincerely,<br>
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:150px;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            """
            
            # Preview di Streamlit (dengan scrollbar agar pas di HP)
            st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)
            st.markdown(html_invoice, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Tombol Download
            st.write("---")
            components.html(f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="unduh()" style="width:100%; padding:15px; background:#4CAF50; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📥 DOWNLOAD PDF SEKARANG</button>
            <script>
            function unduh() {{
                const el = window.parent.document.getElementById('invoice-download-area');
                const opt = {{
                    margin: 0.3,
                    filename: 'INV_{cust}_{tgl}.pdf',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 2, useCORS: true, width: 800 }},
                    jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
                }};
                html2pdf().set(opt).from(el).save();
            }}
            </script>
            """, height=100)

    with tab2:
        st.subheader("➕ Input Data Baru")
        with st.form("add_data"):
            c1, c2 = st.columns(2)
            f_tgl = c1.date_input("Tanggal")
            f_cust = c1.text_input("Customer")
            f_desc = c1.text_input("Barang")
            f_orig = c2.text_input("Origin", "SBY")
            f_dest = c2.text_input("Dest")
            f_kol = c2.number_input("Kolli", 0)
            f_kg = c2.number_input("Weight (Kg)", 1)
            f_hrg = c2.number_input("Harga", 0)
            if st.form_submit_button("Simpan Data"):
                p = { "date": str(f_tgl), "customer": f_cust.upper(), "description": f_desc.upper(), "origin": f_orig.upper(), "destination": f_dest.upper(), "kolli": f_kol, "harga": f_hrg, "weight": f_kg, "total": f_hrg * f_kg }
                requests.post(API_URL, data=json.dumps(p))
                st.success("Data masuk!")
                st.cache_data.clear()
