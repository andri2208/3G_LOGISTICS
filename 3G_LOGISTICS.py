import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", layout="wide")

# CSS untuk hasil cetak yang bersih
st.markdown("""
    <style>
    @media print {
        header, .stSidebar, .stTabs [data-baseweb="tab-list"], .stActionButton, button { display: none !important; }
        .main .block-container { padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONFIG URL & KONEKSI ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw9le3yTcQn3TAevrbOi1s7X-wGJKd-o7n1lN4o8yp7KvmOAHX9GhoGLU8x67IrZWDl/exec"

conn = st.connection("gsheets", type=GSheetsConnection)

def get_image_base64(path):
    import os
    import base64
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return str(int(n))

# Load Gambar-gambar
logo_base = get_image_base64("3G.png")
ttd_base = get_image_base64("TANDA TANGAN.png")
stempel_base = get_image_base64("STEMPEL DAN NAMA.png")

def fetch_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

# --- 3. UI TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Input Data", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("No Resi")
            customer = st.text_input("Customer Name")
            produk = st.text_area("Product Description")
        with col2:
            org = st.text_input("Origin")
            dst = st.text_input("Destination")
            kolli = st.number_input("KOLLI", min_value=1, step=1)
            harga = st.number_input("Harga Satuan", min_value=0)
            berat = st.number_input("Weight (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN DATA"):
            payload = {
                "Tanggal": tgl.strftime('%d-%b-%y'), "Resi": resi, "Pengirim": customer,
                "Produk": produk, "Origin": org, "Destination": dst,
                "Kolli": str(int(kolli)), "Harga": str(int(harga)), "Berat": str(float(berat))
            }
            try:
                res = requests.post(APPS_SCRIPT_URL, json=payload)
                if res.status_code == 200:
                    st.success("Data Berhasil Disimpan!")
                    st.cache_data.clear()
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    st.dataframe(fetch_data(), use_container_width=True)

with tab3:
    st.header("Cetak Invoice")
    
    # 1. Ambil data dari database/sheet
    df_inv = fetch_data()
    
    if not df_inv.empty and 'Resi' in df_inv.columns:
        # 2. Fitur Pilih Nomor Resi
        pilih_resi = st.selectbox("Pilih No Resi untuk Dicetak", df_inv['Resi'].dropna().unique())
        
        # 3. Filter data berdasarkan resi yang dipilih
        data_pilihan = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
        
        # 4. Ambil nilai untuk perhitungan
        # Membersihkan format harga (menghilangkan Rp dan titik)
        h_raw = str(data_pilihan.get('Harga', '0')).split('.')[0]
        harga_angka = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
        
        # Ambil berat
        berat_angka = float(pd.to_numeric(data_pilihan.get('Berat', 0), errors='coerce'))
        
        # Hitung Total
        total_bayar = harga_angka * berat_angka

        # 5. Load Gambar Logo, TTD, dan Stempel (Pastikan file ada di folder app)
        logo_3g = get_image_base64("3G.png")
        ttd_img = get_image_base64("TANDA TANGAN.png")
        stempel_img = get_image_base64("STEMPEL DAN NAMA.png")

        # 6. Susun HTML ke dalam variabel 'html_final'
        html_final = f"""
        <div style="background-color: white; color: black; padding: 40px; border: 1px solid #ddd; font-family: 'Arial'; width: 800px; margin: auto;">
            
            <table style="width: 100%; border: none;">
                <tr>
                    <td style="width: 150px;">
                        <img src="data:image/png;base64,{logo_3g}" width="140">
                    </td>
                    <td style="vertical-align: middle;">
                        <h2 style="margin: 0; color: #1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size: 11px; margin: 5px 0;">
                            Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>
                            Telp: 031-79973432 | Email: finance@3glogistics.com
                        </p>
                    </td>
                    <td style="text-align: right; vertical-align: top;">
                        <h1 style="margin: 0; color: #d62828; font-size: 30px;">INVOICE</h1>
                        <p style="margin: 5px 0;"><b>DATE: {data_pilihan.get('Tanggal','')}</b></p>
                    </td>
                </tr>
            </table>

            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p style="font-size: 14px;"><b>CUSTOMER: {str(data_pilihan.get('Pengirim','')).upper()}</b></p>

            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 12px;">
                <thead style="background-color: #f2f2f2;">
                    <tr>
                        <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                        <th style="border: 1px solid black;">Product Description</th>
                        <th style="border: 1px solid black;">Origin</th>
                        <th style="border: 1px solid black;">Destination</th>
                        <th style="border: 1px solid black;">KOLLI</th>
                        <th style="border: 1px solid black;">HARGA</th>
                        <th style="border: 1px solid black;">WEIGHT</th>
                        <th style="border: 1px solid black;">TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid black; padding: 20px;">{data_pilihan.get('Tanggal','')}</td>
                        <td style="border: 1px solid black; text-align: left; padding-left: 10px;">{data_pilihan.get('Produk','')}</td>
                        <td style="border: 1px solid black;">{data_pilihan.get('Origin','')}</td>
                        <td style="border: 1px solid black;">{data_pilihan.get('Destination','')}</td>
                        <td style="border: 1px solid black;">{data_pilihan.get('Kolli',0)}</td>
                        <td style="border: 1px solid black;">Rp {harga_angka:,}</td>
                        <td style="border: 1px solid black;">{berat_angka} Kg</td>
                        <td style="border: 1px solid black; font-weight: bold;">Rp {total_bayar:,.0f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="text-align: right; margin-top: 25px;">
                <h3 style="margin: 0;">YANG HARUS DI BAYAR: <span style="color: #d62828;">Rp {total_bayar:,.0f}</span></h3>
                <p style="font-size: 13px; margin-top: 5px;"><i>Terbilang: {terbilang(total_bayar)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 50px; font-size: 13px;">
                <tr>
                    <td style="width: 60%; vertical-align: top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia (BCA)<br>
                        No Rek: 6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br><br>
                        <span style="font-size: 11px; color: #555;"><i>NB: Mohon konfirmasi ke Finance 082179799200</i></span>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Gresik, {data_pilihan.get('Tanggal','')}<br>
                        Sincerely,<br>
                        <b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="position: relative; height: 120px; width: 200px; margin: auto;">
                            <img src="data:image/png;base64,{ttd_img}" 
                                 style="position: absolute; width: 110px; left: 45px; top: 10px; z-index: 1;">
                            
                            <img src="data:image/png;base64,{stempel_img}" 
                                 style="position: absolute; width: 160px; left: 20px; top: -5px; z-index: 2; opacity: 0.8;">
                        </div>

                        <br><b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # 7. Tampilkan ke Layar Streamlit
        st.markdown(html_final, unsafe_allow_html=True)
        
        # Tombol Download (Opsional)
        st.download_button("Download Invoice (HTML)", data=html_final, file_name=f"Invoice_{pilih_resi}.html", mime="text/html")
    else:
        st.warning("Data tidak ditemukan atau kolom 'Resi' hilang.")
