import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

# 2. CSS UNTUK TAMPILAN WEB (RESPONSIF HP)
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container { padding: 1rem; }
    .stTabs { margin-top: -15px; }
    /* Supaya di HP bisa di-geser tapi tidak rusak layoutnya */
    .table-responsive { width: 100%; overflow-x: auto; background: #f0f2f6; padding: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN SISTEM
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Masuk"):
            if u == "admin3g" and p == "gama2024":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("Akses Ditolak!")
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

    # UI HEADER
    c1, c2 = st.columns([0.8, 0.2])
    with c2: 
        if st.button("Logout 🚪"): 
            st.session_state['logged_in'] = False
            st.rerun()

    st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)
    tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

    with tab1:
        data = get_data()
        if data:
            df = pd.DataFrame(data)
            pilih = st.selectbox("Pilih Customer:", df['customer'].unique())
            row = df[df['customer'] == pilih].iloc[-1]
            tgl = str(row['date']).split('T')[0]
            total = int(row['total'])
            txt_terbilang = terbilang(total).title() + " Rupiah"

            # --- HTML INVOICE (GARIS NYAMBUNG & KUNCI LEBAR 800PX) ---
            html_invoice = f"""
            <div id="print-area" style="background:white; padding:40px; width:800px; margin:auto; color:black; font-family:Arial, sans-serif;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%; display:block;">
                <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:15px 0; padding:8px; font-weight:bold; font-size:24px;">INVOICE</div>
                
                <table style="width:100%; font-weight:bold; font-size:16px; margin-bottom:15px; border-collapse: collapse;">
                    <tr><td>CUSTOMER : {row['customer']}</td><td style="text-align:right;">DATE : {tgl}</td></tr>
                </table>

                <table style="width:100%; border-collapse:collapse; border:2px solid black; border-spacing:0;">
                    <tr style="background:#316395; color:white; text-align:center; font-size:13px;">
                        <th style="border:1px solid black; padding:10px;">Date of Load</th>
                        <th style="border:1px solid black;">Description</th>
                        <th style="border:1px solid black;">Origin</th>
                        <th style="border:1px solid black;">Dest</th>
                        <th style="border:1px solid black;">KOLLI</th>
                        <th style="border:1px solid black;">HARGA</th>
                        <th style="border:1px solid black;">WEIGHT</th>
                    </tr>
                    <tr style="text-align:center; font-size:13px;">
                        <td style="border:1px solid black; padding:20px;">{tgl}</td>
                        <td style="border:1px solid black;">{row['description']}</td>
                        <td style="border:1px solid black;">{row['origin']}</td>
                        <td style="border:1px solid black;">{row['destination']}</td>
                        <td style="border:1px solid black;">{row['kolli']}</td>
                        <td style="border:1px solid black;">Rp {int(row['harga']):,}</td>
                        <td style="border:1px solid black;">{row['weight']} Kg</td>
                    </tr>
                    <tr style="font-weight:bold; background:#f2f2f2; text-align:center; font-size:13px;">
                        <td colspan="6" style="border:1px solid black; padding:12px;">YANG HARUS DI BAYAR</td>
                        <td style="border:1px solid black;">Rp {total:,}</td>
                    </tr>
                    <tr>
                        <td colspan="7" style="border:1px solid black; padding:12px; font-size:14px; font-style:italic;">
                            <b>Terbilang :</b> {txt_terbilang}
                        </td>
                    </tr>
                </table>

                <br><br>
                <table style="width:100%; font-size:14px; line-height:1.6;">
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
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:160px; margin:10px 0;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            """
            
            # Tampilkan Preview
            st.markdown('<div class="table-responsive">', unsafe_allow_html=True)
            st.markdown(html_invoice, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # SCRIPT DOWNLOAD PDF
            st.write("---")
            components.html(f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <button onclick="downloadPDF()" style="width:100%; padding:18px; background:#4CAF50; color:white; border:none; border-radius:10px; font-weight:bold; font-size:18px; cursor:pointer;">📥 DOWNLOAD INVOICE SEKARANG</button>
            <script>
            function downloadPDF() {{
                const element = window.parent.document.getElementById('print-area');
                const opt = {{
                    margin: 0.3,
                    filename: 'INV_{pilih}_{tgl}.pdf',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 2, useCORS: true, width: 800 }},
                    jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
            </script>
            """, height=100)

    with tab2:
        st.subheader("➕ Tambah Data Pengiriman")
        with st.form("input_data", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_tgl = c1.date_input("Tanggal")
            f_cust = c1.text_input("Customer")
            f_desc = c1.text_input("Barang")
            f_orig = c2.text_input("Origin", "SBY")
            f_dest = c2.text_input("Destination")
            f_kol = c2.number_input("Kolli", 0)
            f_kg = c2.number_input("Weight (Kg)", 1)
            f_hrg = c2.number_input("Harga Satuan", 0)
            if st.form_submit_button("🚀 SIMPAN DATA"):
                p = { "date": str(f_tgl), "customer": f_cust.upper(), "description": f_desc.upper(), "origin": f_orig.upper(), "destination": f_dest.upper(), "kolli": f_kol, "harga": f_hrg, "weight": f_kg, "total": f_hrg * f_kg }
                requests.post(API_URL, data=json.dumps(p))
                st.success("Data Berhasil Disimpan!")
                st.cache_data.clear()
