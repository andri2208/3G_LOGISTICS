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

# --- CSS CUSTOM UNTUK MEMPERTEBAL TEKS DI ATAS KOLOM ---
st.markdown("""
    <style>
    /* Mempertebal semua label (teks di atas kolom) */
    .stWidgetLabel p {
        font-weight: 900 !important; /* Sangat Tebal */
        font-size: 16px !important;
        color: #1E1E1E !important;
        margin-bottom: 8px !important;
    }
    
    /* Memberi warna latar pada kolom input agar menonjol */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        background-color: #F8F9FA !important;
        border: 2px solid #D1D5DB !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* Warna saat kolom diklik */
    .stTextInput input:focus {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice (A5)", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.info("Sedang mengambil data...")
    else:
        df = pd.DataFrame(data)
        selected_cust = st.selectbox("Pilih Nama Customer:", sorted(df['customer'].unique()))
        row = df[df['customer'] == selected_cust].iloc[-1]
        
        b_val = extract_number(row['weight'])
        h_val = extract_number(row['harga'])
        t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
        
        tgl_raw = str(row['date']).split('T')[0]
        tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        kata_terbilang = terbilang(t_val) + " Rupiah"

        invoice_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: white; }}
                .container {{ background: white; padding: 15px; max-width: 750px; margin: auto; border: 1px solid #ccc; }}
                .header-img {{ width: 100%; height: auto; }}
                .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 10px 0; padding: 5px; font-weight: bold; font-size: 1.2rem; }}
                .info-table {{ width: 100%; margin-bottom: 10px; font-size: 12px; font-weight: bold; }}
                .data-table {{ width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; }}
                .data-table th, .data-table td {{ border: 1px solid black; padding: 8px; }}
                .data-table th {{ background-color: #eee; }}
                .terbilang {{ border: 1px solid black; padding: 8px; margin-top: 10px; font-size: 11px; font-style: italic; }}
                .footer {{ width: 100%; margin-top: 20px; font-size: 11px; }}
                .btn-download {{ width: 100%; background: #28a745; color: white; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 20px; font-size: 16px; }}
            </style>
        </head>
        <body>
            <div class="container" id="invoice-card">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" class="header-img">
                <div class="title">INVOICE</div>
                <table class="info-table">
                    <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                </table>
                <div style="overflow-x: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td><td>{row['kolli']}</td>
                                <td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td>Rp {t_val:,}</td>
                            </tr>
                            <tr style="font-weight:bold; background:#f9f9f9;">
                                <td colspan="6" style="text-align:right;">YANG HARUS DIBAYAR</td><td>Rp {t_val:,}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                
                <table class="footer">
                    <tr>
                        <td style="width:60%; vertical-align: top;">
                            <b>TRANSFER TO :</b><br>
                            Bank Central Asia <b>6720422334</b><br>
                            A/N <b>ADITYA GAMA SAPUTRI</b><br><br>
                            <i>NB : Jika sudah transfer mohon konfirmasi ke<br>
                            Finance <b>082179799200</b></i>
                        </td>
                        <td style="text-align:center; vertical-align: top;">
                            Sincerely,<br>
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:110px;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            <button class="btn-download" onclick="downloadA5()">📥 DOWNLOAD INVOICE (UKURAN A5)</button>

            <script>
                function downloadA5() {{
                    const element = document.getElementById('invoice-card');
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
        </body>
        </html>
        """
        components.html(invoice_html, height=850, scrolling=True)

with tab2:
    st.markdown("### ➕ Input Data Pengiriman Baru")
    with st.form("form_db", clear_on_submit=True):
        col1, col2 = st.columns(2)
        v_tgl = col1.date_input("TANGGAL PENGIRIMAN", datetime.now())
        v_cust = col1.text_input("NAMA CUSTOMER")
        v_desc = col1.text_input("DESKRIPSI BARANG")
        v_orig = col2.text_input("ORIGIN (ASAL)", value="SBY")
        v_dest = col2.text_input("DESTINATION (TUJUAN)")
        v_kol = col2.text_input("JUMLAH KOLLI (Contoh: 10 Box)")
        v_kg = col2.text_input("WEIGHT / BERAT (Angka Saja)")
        v_hrg = col2.number_input("HARGA SATUAN (Rp)", 0)
        
        st.markdown("---")
        if st.form_submit_button("💾 SIMPAN DATA KE GOOGLE SHEETS"):
            w_num = extract_number(v_kg)
            total_db = int(w_num * v_hrg) if w_num > 0 else int(v_hrg)
            payload = {
                "date": str(v_tgl), "customer": v_cust.upper(), "description": v_desc.upper(),
                "origin": v_orig.upper(), "destination": v_dest.upper(), "kolli": v_kol,
                "harga": v_hrg, "weight": v_kg, "total": total_db
            }
            try:
                requests.post(API_URL, data=json.dumps(payload))
                st.success(f"✅ Berhasil Disimpan! Total Tagihan Otomatis: Rp {total_db:,}")
                st.cache_data.clear()
            except:
                st.error("❌ Gagal terhubung ke database.")
