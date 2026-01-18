import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="3G Logistics System", layout="centered", initial_sidebar_state="collapsed")

# URL API GAS (Google Apps Script)
API_URL = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

# Fungsi Terbilang Sederhana
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

@st.cache_data(ttl=5)
def get_data():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except: 
        return []

# CSS untuk memastikan PDF rapi dan gambar tidak terpotong
st.markdown("""
    <style>
    #invoice-preview img { max-width: 100%; height: auto; }
    [data-testid="stForm"] { border: 1px solid #ddd; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Header Aplikasi
st.image("https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png", use_container_width=True)

tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

with tab1:
    data = get_data()
    if not data:
        st.warning("Menunggu data dari Database...")
    else:
        df = pd.DataFrame(data)
        # Menghapus duplikat nama customer untuk dropdown
        list_cust = sorted(df['customer'].unique())
        selected_cust = st.selectbox("Pilih Nama Customer:", list_cust)
        
        # Ambil data terbaru untuk customer tersebut
        row = df[df['customer'] == selected_cust].iloc[-1]
        
        # Format Data
        tgl_raw = str(row['date']).split('T')[0]
        tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        total_harga = int(row['total'])
        teks_terbilang = terbilang(total_harga).strip() + " Rupiah"
        nama_file = f"Invoice_{selected_cust}_{tgl_raw}.pdf"

        # HTML DESAIN (Menggunakan format tabel sesuai lampiran)
        html_desain = f"""
        <div id="invoice-box" style="background-color:white; padding:20px; color:black; font-family:'Arial', sans-serif; border:1px solid #eee;">
            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
            
            <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:15px 0; padding:5px;">
                <h2 style="margin:0; letter-spacing: 2px;">INVOICE</h2>
            </div>

            <div style="display:flex; justify-content:space-between; margin-bottom:15px; font-weight:bold; font-size:14px;">
                <span>CUSTOMER : {row['customer']}</span>
                <span>DATE : {tgl_indo}</span>
            </div>

            <table style="width:100%; border-collapse:collapse; border:1.5px solid black; font-size:12px;">
                <thead>
                    <tr style="background-color:#f2f2f2; text-align:center;">
                        <th style="border:1px solid black; padding:8px;">Date of Load</th>
                        <th style="border:1px solid black; padding:8px;">Product Description</th>
                        <th style="border:1px solid black; padding:8px;">Origin</th>
                        <th style="border:1px solid black; padding:8px;">Dest</th>
                        <th style="border:1px solid black; padding:8px;">KOLLI</th>
                        <th style="border:1px solid black; padding:8px;">HARGA</th>
                        <th style="border:1px solid black; padding:8px;">WEIGHT</th>
                        <th style="border:1px solid black; padding:8px;">TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="text-align:center;">
                        <td style="border:1px solid black; padding:10px;">{tgl_indo}</td>
                        <td style="border:1px solid black; padding:10px;">{row['description']}</td>
                        <td style="border:1px solid black; padding:10px;">{row['origin']}</td>
                        <td style="border:1px solid black; padding:10px;">{row['destination']}</td>
                        <td style="border:1px solid black; padding:10px;">{row['kolli']}</td>
                        <td style="border:1px solid black; padding:10px;">Rp {int(row['harga']):,}</td>
                        <td style="border:1px solid black; padding:10px;">{row['weight']}</td>
                        <td style="border:1px solid black; padding:10px;">Rp {total_harga:,}</td>
                    </tr>
                    <tr style="font-weight:bold;">
                        <td colspan="7" style="border:1px solid black; text-align:right; padding:8px;">YANG HARUS DI BAYAR</td>
                        <td style="border:1px solid black; text-align:center; padding:8px; background-color:#f9f9f9;">Rp {total_harga:,}</td>
                    </tr>
                </tbody>
            </table>

            <div style="margin-top:10px; padding:10px; border:1px solid black; font-style:italic; font-size:12px;">
                <b>Terbilang :</b> {teks_terbilang}
            </div>

            <div style="margin-top:30px; display:flex; justify-content:space-between; font-size:12px;">
                <div style="width:60%;">
                    <b style="text-decoration:underline;">TRANSFER TO :</b><br>
                    Bank Central Asia (BCA)<br>
                    No Rek: <b>6720422334</b><br>
                    A/N: <b>ADITYA GAMA SAPUTRI</b><br>
                    <p style="font-size:10px; margin-top:5px;">NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</p>
                </div>
                <div style="width:35%; text-align:center;">
                    Sincerely,<br>
                    PT. GAMA GEMAH GEMILANG<br>
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:140px; margin:5px 0;"><br>
                    <b><u>KELVINITO JAYADI</u></b><br>
                    DIREKTUR
                </div>
            </div>
        </div>
        """

        # Tampilkan Preview di Streamlit
        st.markdown(html_desain, unsafe_allow_html=True)

        # Tombol Download menggunakan JavaScript
        st.write("---")
        pdf_script = f"""
        <html>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <script>
            function generatePDF() {{
                const element = window.parent.document.getElementById('invoice-box');
                const opt = {{
                    margin: 0.2,
                    filename: '{nama_file}',
                    image: {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas: {{ scale: 3, useCORS: true, logging: false }},
                    jsPDF: {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
            </script>
            <button onclick="generatePDF()" style="width:100%; background-color:#1e3d59; color:white; padding:15px; border:none; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">
                📥 DOWNLOAD INVOICE SEBAGAI PDF
            </button>
        </html>
        """
        components.html(pdf_script, height=80)

with tab2:
    st.subheader("➕ Input Data Baru")
    with st.form("form_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        in_tgl = c1.date_input("Tanggal Transaksi", datetime.now())
        in_cust = c1.text_input("Nama Customer")
        in_desc = c1.text_input("Keterangan Barang")
        in_orig = c2.text_input("Origin (Asal)", value="SBY")
        in_dest = c2.text_input("Destination (Tujuan)")
        in_kol = c2.text_input("KOLLI (e.g. 10 BOX)")
        in_kg = c2.text_input("Weight/Qty (e.g. 500 Kg)")
        in_hrg = c2.number_input("Harga Satuan", 0)
        in_total = c2.number_input("Total Tagihan (Rp)", 0)
        
        st.info("Catatan: Gunakan 'Total Tagihan' untuk nilai akhir yang muncul di invoice.")
        
        if st.form_submit_button("SIMPAN KE DATABASE"):
            if not in_cust or not in_dest:
                st.error("Nama Customer dan Tujuan wajib diisi!")
            else:
                payload = {
                    "date": str(in_tgl),
                    "customer": in_cust.upper(),
                    "description": in_desc.upper(),
                    "origin": in_orig.upper(),
                    "destination": in_dest.upper(),
                    "kolli": in_kol,
                    "harga": in_hrg,
                    "weight": in_kg,
                    "total": in_total if in_total > 0 else (in_hrg)
                }
                try:
                    response = requests.post(API_URL, data=json.dumps(payload), timeout=15)
                    st.success(f"Data {in_cust.upper()} Berhasil Disimpan!")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Gagal terhubung ke Database: {e}")
