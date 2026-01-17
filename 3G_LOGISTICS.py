import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# --- 2. FUNGSI LOAD GAMBAR ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. FUNGSI TERBILANG ---
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

# --- 4. DATABASE SESSION (Pastikan Nama Kolom Konsisten) ---
if 'db' not in st.session_state:
    # Kita gunakan nama kolom yang jelas: No_Resi, Tanggal, Customer, Barang, Origin, Destination, Harga, Berat
    st.session_state.db = pd.DataFrame(columns=['No_Resi','Tanggal','Customer','Barang','Origin','Destination','Harga','Berat'])

# --- 5. NAVIGASI (DENGAN HEADER GAMBAR) ---
# Menampilkan gambar header sebagai pengganti judul teks
if os.path.exists("HEADER-INVOICE.PNG"):
    st.image("HEADER-INVOICE.PNG", use_container_width=True)
else:
    st.title("3G LOGISTICS SYSTEM") # Cadangan jika file gambar tidak ditemukan

# Navigasi Tab
tab1, tab2 = st.tabs(["📝 INPUT DATA", "🖨️ CETAK INVOICE"])


# --- TAB INPUT ---
with tab1:
    with st.form("f1", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            in_resi = st.text_input("No Resi")
            in_tgl = st.date_input("Tanggal", value=datetime.now())
            in_cust = st.text_input("Customer")
            in_barang = st.text_area("Deskripsi Barang")
        with c2:
            in_asal = st.text_input("Origin", value="SBY")
            in_tujuan = st.text_input("Destination", value="MEDAN")
            in_harga = st.number_input("Harga", min_value=0)
            in_berat = st.number_input("Berat (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN DATA ✅"):
            if in_resi and in_cust:
                # Memasukkan data dengan nama kolom yang PASTI sama dengan database
                row = pd.DataFrame([{
                    'No_Resi': in_resi,
                    'Tanggal': in_tgl.strftime('%d-%b-%y'),
                    'Customer': in_cust,
                    'Barang': in_barang,
                    'Origin': in_asal,
                    'Destination': in_tujuan,
                    'Harga': in_harga,
                    'Berat': in_berat
                }])
                st.session_state.db = pd.concat([st.session_state.db, row], ignore_index=True)
                st.success(f"Data {in_resi} Berhasil Disimpan!")
            else:
                st.error("Nomor Resi dan Customer wajib diisi!")

# --- TAB CETAK ---
with tab2:
    if st.session_state.db.empty:
        st.warning("Data kosong. Harap input data terlebih dahulu.")
    else:
        pilih_resi = st.selectbox("Pilih No Resi", st.session_state.db['No_Resi'].unique())
        # Ambil baris data
        d = st.session_state.db[st.session_state.db['No_Resi'] == pilih_resi].iloc[0]
        
        # Perhitungan
        total_rp = float(d['Harga']) * float(d['Berat'])
        
        # Load Gambar
        h_img = get_image_base64("HEADER-INVOCE.PNG")
        f_img = get_image_base64("STEMPEL-TANDA-TANGAN.PNG")

        # HTML INVOICE (Memanggil nama kolom yang sudah diperbaiki)
        invoice_html = f"""
        <div style="background:white; color:black; padding:20px; font-family:Arial; width:800px; margin:auto; border:1px solid #eee;">
            <img src="data:image/png;base64,{h_img}" style="width:100%;">
            <div style="text-align:right; margin-top:10px;">
                <h1 style="color:red; margin:0; font-size:35px;">INVOICE</h1>
                <p>DATE: {d['Tanggal']}</p>
            </div>
            <p><b>CUSTOMER: {str(d['Customer']).upper()}</b></p>
            <table style="width:100%; border-collapse:collapse; border:1px solid black; text-align:center; font-size:12px;">
                <tr style="background:#f2f2f2;">
                    <th style="border:1px solid black; padding:8px;">Product Description</th>
                    <th style="border:1px solid black;">Origin</th>
                    <th style="border:1px solid black;">Destination</th>
                    <th style="border:1px solid black;">Harga</th>
                    <th style="border:1px solid black;">Weight</th>
                    <th style="border:1px solid black;">Total</th>
                </tr>
                <tr>
                    <td style="border:1px solid black; padding:15px; text-align:left;">{d['Barang']}</td>
                    <td style="border:1px solid black;">{d['Origin']}</td>
                    <td style="border:1px solid black;">{d['Destination']}</td>
                    <td style="border:1px solid black;">Rp {d['Harga']:,}</td>
                    <td style="border:1px solid black;">{d['Berat']} Kg</td>
                    <td style="border:1px solid black;"><b>Rp {total_rp:,.0f}</b></td>
                </tr>
            </table>
            <div style="text-align:right; margin-top:20px;">
                <h3 style="margin:0;">YANG HARUS DIBAYAR: <span style="color:red; font-size:22px;">Rp {total_rp:,.0f}</span></h3>
                <p style="font-size:12px;"><i>Terbilang: {terbilang(total_rp)} Rupiah</i></p>
            </div>
            <table style="width:100%; margin-top:30px; font-size:13px;">
                <tr>
                    <td style="width:60%;"><b>TRANSFER TO :</b><br>Bank BCA | 6720422334 | A/N ADITYA GAMA SAPUTRI</td>
                    <td style="text-align:center;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        <img src="data:image/png;base64,{f_img}" width="180"><br>
                        <b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        st.markdown(invoice_html, unsafe_allow_html=True)

