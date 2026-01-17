import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os

# --- 1. KONFIGURASI HALAMAN & FAVICON ---
st.set_page_config(
    page_title="3G LOGISTICS - System",
    page_icon="3G.png",
    layout="wide"
)

# --- 2. FUNGSI TOOLS ---
def get_image_base64(path):
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
    return str(n)

# Load Gambar (Pastikan file-file ini ada di GitHub)
logo_base64 = get_image_base64("3G.png")
stempel_base64 = get_image_base64("STEMPEL.png")
ttd_base64 = get_image_base64("TTD.png")

# --- 3. TAMPILAN HEADER DASHBOARD (PRESISI) ---
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 20px; padding: 10px 0;">
        <img src="data:image/png;base64,{logo_base64}" width="100">
        <div>
            <h1 style="margin: 0; padding: 0; line-height: 1; color: #1a3d8d;">PT. GAMA GEMAH GEMILANG</h1>
            <p style="margin: 5px 0 0 0; font-size: 18px; color: #d62828; font-weight: bold;">Management Logistics System</p>
        </div>
    </div>
    <hr style="border: none; border-top: 3px solid #1a3d8d; margin-top: 10px; margin-bottom: 25px;">
    """, 
    unsafe_allow_html=True
)

# --- 4. DATABASE SEDERHANA (CONTOH) ---
# Bagian ini bisa Anda sambungkan ke Google Sheets atau CSV Anda
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Tanggal', 'Resi', 'Pengirim', 'Produk', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'])

# --- 5. TABS ---
tab1, tab2, tab3 = st.tabs(["Tambah Data", "Lihat Database", "Cetak Invoice"])

with tab1:
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("Nomor Resi")
            pengirim = st.text_input("Nama Customer")
        with col2:
            produk = st.text_input("Deskripsi Barang")
            origin = st.text_input("Origin")
            dest = st.text_input("Destination")
        
        c1, c2, c3 = st.columns(3)
        kolli = c1.number_input("Kolli", min_value=0)
        harga = c2.number_input("Harga Satuan", min_value=0)
        berat = c3.number_input("Berat (Kg)", min_value=0)
        
        submit = st.form_submit_button("Simpan Data")
        if submit:
            new_data = pd.DataFrame([[tgl.strftime('%d-%b-%y'), resi, pengirim, produk, origin, dest, kolli, harga, berat]], 
                                    columns=st.session_state.db.columns)
            st.session_state.db = pd.concat([st.session_state.db, new_data], ignore_index=True)
            st.success("Data Berhasil Disimpan!")

with tab2:
    st.dataframe(st.session_state.db, use_container_width=True)

with tab3:
    if not st.session_state.db.empty:
        pilih_resi = st.selectbox("Pilih Nomor Resi untuk Invoice", st.session_state.db['Resi'].unique())
        d = st.session_state.db[st.session_state.db['Resi'] == pilih_resi].iloc[0]
        
        # Perhitungan
        harga_float = float(d['Harga'])
        total_float = harga_float * float(d['Berat'])
        
        # --- HTML INVOICE YANG SUDAH DIPERBAIKI ---
        st.markdown(f"""
        <div style="border: 1px solid #000; padding: 30px; background-color: white; color: black; font-family: Arial;">
            <table style="width:100%; border:none; border-collapse: collapse;">
                <tr>
                    <td style="width:120px; border:none; vertical-align: middle;">
                        <img src="data:image/png;base64,{logo_base64}" style="width:110px;">
                    </td>
                    <td style="border:none; padding-left: 20px; vertical-align: middle; text-align: left;">
                        <h2 style="margin:0; color: #1a3d8d; font-size: 24px;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:2px 0; color: black; line-height: 1.4;">
                            Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti,<br>
                            Gresik, Jawa Timur. Telp: 031-79973432 | Email: finance@3glogistics.com
                        </p>
                    </td>
                    <td style="border:none; text-align:right; vertical-align: middle;">
                        <h1 style="margin:0; color: #d62828; font-size: 32px;">INVOICE</h1>
                        <p style="margin:0; font-weight: bold;"># {d['Resi']}</p>
                    </td>
                </tr>
            </table>
            
            <hr style="border: none; border-top: 3px solid #1a3d8d; margin-top: 10px; margin-bottom: 20px;">
            
            <table style="width:100%; border:none;">
                <tr>
                    <td style="border:none;"><strong>DITUJUKAN KEPADA:</strong><br>{str(d['Pengirim']).upper()}</td>
                    <td style="text-align:right; border:none; vertical-align: top;">
                        <strong>TANGGAL:</strong> {d['Tanggal']}<br>
                        <strong>METODE:</strong> Darat / Laut
                    </td>
                </tr>
            </table>
            
            <br>
            <table style="width:100%; border-collapse: collapse; text-align: center; border: 1px solid black;">
                <tr style="background-color: #1a3d8d; color: white;">
                    <th style="border: 1px solid black; padding:8px;">Deskripsi Barang</th>
                    <th style="border: 1px solid black; padding:8px;">Origin</th>
                    <th style="border: 1px solid black; padding:8px;">Destination</th>
                    <th style="border: 1px solid black; padding:8px;">KOLLI</th>
                    <th style="border: 1px solid black; padding:8px;">BERAT</th>
                    <th style="border: 1px solid black; padding:8px;">HARGA</th>
                    <th style="border: 1px solid black; padding:8px;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding:15px; text-align: left;">{d['Produk']}</td>
                    <td style="border: 1px solid black;">{d['Origin']}</td>
                    <td style="border: 1px solid black;">{d['Destination']}</td>
                    <td style="border: 1px solid black;">{d['Kolli']}</td>
                    <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                    <td style="border: 1px solid black;">Rp {harga_float:,.0f}</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total_float:,.0f}</td>
                </tr>
            </table>
            
            <div style="margin-top: 20px; text-align: right;">
                <h3 style="margin:0; color: #d62828;">YANG HARUS DIBAYAR: Rp {total_float:,.0f}</h3>
            </div>
            
            <div style="margin-top: 10px; padding: 10px; background-color: #f2f2f2; border-left: 5px solid #d62828;">
                <strong>Terbilang:</strong> <em>{terbilang(total_float)} Rupiah</em>
            </div>

            <table style="width:100%; border:none; margin-top: 40px;">
                <tr>
                    <td style="width:60%; border:none; vertical-align: top; font-size: 13px;">
                        <strong>INFORMASI PEMBAYARAN:</strong><br>
                        Bank Central Asia (BCA)<br>
                        No. Rekening: <strong>6720422334</strong><br>
                        A/N: <strong>ADITYA GAMA SAPUTRI</strong>
                    </td>
                    <td style="text-align: center; border:none;">
                        Gresik, {d['Tanggal']}<br>
                        PT. GAMA GEMAH GEMILANG<br><br>
                        <div style="position: relative; display: inline-block;">
                            <img src="data:image/png;base64,{stempel_base64}" style="width:180px;">
                            <img src="data:image/png;base64,{ttd_base64}" style="width:100px; position: absolute; top: 10px; left: 50%; transform: translateX(-50%);">
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("Gunakan Ctrl+P (Windows) atau Cmd+P (Mac) untuk menyimpan sebagai PDF.")
    else:
        st.warning("Silakan isi data terlebih dahulu di tab 'Tambah Data'.")
