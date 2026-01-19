import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics Pro", layout="wide")

# 2. CSS (MEMBERSIHKAN TAMPILAN & RESPONSIVE)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    div[data-baseweb="tab-list"] { flex-wrap: wrap !important; gap: 10px !important; border-bottom: 4px solid #B8860B !important; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6 !important; border-radius: 8px !important; }
    .stTabs [aria-selected="true"] { background-color: #719dc9 !important; }
    .stTabs [data-baseweb="tab"] p { color: black !important; font-weight: 900 !important; }
    [data-testid="stForm"] { background-color: #719dc9 !important; border-radius: 15px !important; border: 5px solid #B8860B !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI UTAMA
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

# Tab 3: Fake Invoice (Format yang Bapak mau tanpa [cite])
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png", width=420)
tab1, tab2, tab3 = st.tabs(["📄 CETAK INVOICE", "➕ TAMBAH DATA", "🎭 FAKE INVOICE"])

with tab3:
    st.markdown("<h3 style='color: black; text-align: center;'>CETAK INVOICE MANUAL (BERSIH)</h3>", unsafe_allow_html=True)
    with st.form("fake_form"):
        f1, f2, f3 = st.columns(3)
        fk_no = f1.text_input("NOMOR INVOICE", "3G/INV/2026/002")
        fk_cust = f2.text_input("NAMA CUSTOMER", "ZENTRUP")
        fk_tgl = f3.date_input("TANGGAL", datetime.now())
        f4, f5, f6 = st.columns(3)
        fk_item = f4.text_input("ITEM", "BARANG PAKET")
        fk_orig = f5.text_input("ORIGIN", "SBY")
        fk_dest = f6.text_input("DESTINATION", "MINAHASA")
        f7, f8, f9 = st.columns(3)
        fk_kol = f7.text_input("KOLLI", "3")
        fk_harga = f8.number_input("HARGA SATUAN", value=8500)
        fk_weight = f9.number_input("WEIGHT", value=479)
        
        # Hitung Total Otomatis
        total_bayar = fk_harga * fk_weight
        
        if st.form_submit_button("✨ GENERATE INVOICE BERSIH"):
            terbilang_txt = terbilang(total_bayar) + " Rupiah"
            invoice_html = f"""
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.min.js"></script>
            <div id="inv" style="background: white; padding: 25px; width: 750px; margin: auto; color: black; font-family: Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" style="width:100%;">
                <div style="text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px;">INVOICE</div>
                
                <table style="width: 100%; font-size: 14px; font-weight: bold; margin-bottom: 10px;">
                    <tr><td>CUSTOMER: {fk_cust.upper()}</td><td style="text-align:right;">NO: {fk_no}</td></tr>
                    <tr><td>DATE: {fk_tgl.strftime('%d/%m/%Y')}</td><td style="text-align:right;">STATUS: BELUM BAYAR</td></tr>
                </table>

                <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: center;">
                    <tr style="border: 1px solid black; background: #eee;">
                        <th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th>
                    </tr>
                    <tr style="border: 1px solid black;">
                        <td>{fk_item.upper()}</td><td>{fk_orig.upper()}</td><td>{fk_dest.upper()}</td>
                        <td>{fk_kol}</td><td>Rp {fk_harga:,}</td><td>{fk_weight}</td><td style="font-weight:bold;">Rp {total_bayar:,}</td>
                    </tr>
                    <tr style="font-weight:bold; border: 1px solid black;">
                        <td colspan="6" style="text-align:right; padding-right: 10px;">TOTAL BAYAR</td>
                        <td>Rp {total_bayar:,}</td>
                    </tr>
                </table>

                <div style="border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 13px;">
                    <b>Terbilang:</b> {terbilang_txt}
                </div>

                <table style="width: 100%; margin-top: 30px; font-size: 13px;">
                    <tr>
                        <td style="width:60%;">
                            <b>TRANSFER TO :</b><br>
                            BCA <b>6720422334</b><br>
                            <b>ADITYA GAMA SAPUTRI</b><br><br>
                            <small>NB: Konfirmasi Finance: 082179799200</small>
                        </td>
                        <td style="text-align:center;">
                            Sincerely,<br>
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            <button style="width: 100%; max-width: 750px; display: block; margin: 20px auto; background: #49bf59; color: white; padding: 15px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer;" onclick="savePDF()">📥 DOWNLOAD PDF SEKARANG</button>
            <script>
                function savePDF() {{
                    const e = document.getElementById('inv');
                    html2pdf().set({{ 
                        margin: 0.2, 
                        filename: 'Invoice_{fk_cust}.pdf', 
                        html2canvas: {{ scale: 2 }}, 
                        jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} 
                    }}).from(e).save();
                }}
            </script>
            """
            components.html(invoice_html, height=850, scrolling=True)
