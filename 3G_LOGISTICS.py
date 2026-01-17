import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64
from datetime import datetime
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS - System", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
# MASUKKAN URL GOOGLE SHEETS KAMU DI SINI
URL_SHEET = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def muat_data():
    try:
        df = conn.read(spreadsheet=URL_SHEET, usecols=list(range(11)))
        df = df.dropna(how="all") # Hapus baris kosong
        # Pastikan kolom angka dibaca dengan benar
        kolom_angka = ["Kolli", "Berat (kg)", "Harga Satuan", "Total Biaya"]
        for col in kolom_angka:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df.fillna('')
    except:
        return pd.DataFrame(columns=["Tanggal", "Resi", "Pengirim", "Penerima", "Produk", "Origin", "Destination", "Kolli", "Berat (kg)", "Harga Satuan", "Total Biaya"])

# --- FUNGSI TERBILANG ---
def terbilang(n):
    n = int(n)
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[n]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return "Angka terlalu besar"

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- APLIKASI UTAMA ---
st.title("🚚 3G LOGISTICS - Management System")

if 'df' not in st.session_state:
    st.session_state.df = muat_data()

tab1, tab2, tab3 = st.tabs(["➕ Input Pengiriman", "📋 Database (Google Sheets)", "📄 Cetak Invoice"])

with tab1:
    with st.form("form_input", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No. Resi")
            pengirim = st.text_input("Nama Customer (Pengirim)")
            produk = st.text_input("Deskripsi Produk")
            origin = st.text_input("Origin")
        with c2:
            penerima = st.text_input("Nama Penerima")
            destination = st.text_input("Destination")
            kolli = st.number_input("KOLLI", min_value=1, value=1)
            berat = st.number_input("Weight (Kg)", min_value=1, value=1)
            harga_satuan = st.number_input("Harga Satuan (Rp)", min_value=0, value=0)
        
        if st.form_submit_button("Simpan Data ke Cloud"):
            total = berat * harga_satuan
            data_baru = pd.DataFrame([{
                "Tanggal": datetime.now().strftime("%d-%b-%y"),
                "Resi": resi, "Pengirim": pengirim, "Penerima": penerima,
                "Produk": produk, "Origin": origin, "Destination": destination,
                "Kolli": kolli, "Berat (kg)": berat, "Harga Satuan": harga_satuan, "Total Biaya": total
            }])
            
            # Gabungkan dan Update ke Google Sheets
            df_update = pd.concat([st.session_state.df, data_baru], ignore_index=True)
            conn.update(spreadsheet=URL_SHEET, data=df_update)
            st.session_state.df = df_update
            st.success("Data Berhasil Disimpan ke Google Sheets!")
            st.rerun()

with tab2:
    st.subheader("📋 Data Terintegrasi Google Sheets")
    if st.button("Refresh Data"):
        st.session_state.df = muat_data()
    st.dataframe(st.session_state.df, use_container_width=True)

with tab3:
    st.subheader("📄 Preview & Cetak Invoice")
    if not st.session_state.df.empty:
        resi_sel = st.selectbox("Pilih Nomor Resi", st.session_state.df["Resi"].unique())
        
        if resi_sel:
            d = st.session_state.df[st.session_state.df["Resi"] == resi_sel].iloc[0]
            logo = get_image_base64("LOGO INVOICE.png")
            ttd = get_image_base64("TANDA TANGAN.png")
            stempel = get_image_base64("STEMPEL DAN NAMA.png")
            
            total_val = float(d['Total Biaya'])

            st.markdown(f"""
            <div style="border: 1px solid #000; padding: 30px; background-color: white; color: black; font-family: Arial;">
                <table style="width:100%; border:none;">
                    <tr>
                        <td style="width:30%; border:none;"><img src="data:image/png;base64,{logo}" style="width:180px;"></td>
                        <td style="border:none; text-align:left;">
                            <h2 style="margin:0;">PT. GAMA GEMAH GEMILANG</h2>
                            <p style="font-size:11px; margin:0;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik, Jawa Timur. Telp 031-79973432</p>
                        </td>
                    </tr>
                </table>
                <hr style="border: 1px solid black;">
                <table style="width:100%; border:none;">
                    <tr>
                        <td style="border:none;"><strong>CUSTOMER:</strong> {str(d['Pengirim']).upper()}</td>
                        <td style="text-align:right; border:none;"><strong>INVOICE</strong></td>
                    </tr>
                    <tr><td style="border:none;"></td><td style="text-align:right; border:none;">DATE: {d['Tanggal']}</td></tr>
                </table>
                <br>
                <table style="width:100%; border-collapse: collapse; text-align: center; border: 1px solid black;">
                    <tr style="background-color: #eee; border: 1px solid black;">
                        <th style="border: 1px solid black; padding:5px;">Date of Load</th>
                        <th style="border: 1px solid black; padding:5px;">Product Description</th>
                        <th style="border: 1px solid black; padding:5px;">Origin</th>
                        <th style="border: 1px solid black; padding:5px;">Destination</th>
                        <th style="border: 1px solid black; padding:5px;">KOLLI</th>
                        <th style="border: 1px solid black; padding:5px;">HARGA</th>
                        <th style="border: 1px solid black; padding:5px;">WEIGHT</th>
                        <th style="border: 1px solid black; padding:5px;">TOTAL</th>
                    </tr>
                    <tr>
                        <td style="border: 1px solid black; padding:10px;">{d['Tanggal']}</td>
                        <td style="border: 1px solid black;">{d['Produk']}</td>
                        <td style="border: 1px solid black;">{d['Origin']}</td>
                        <td style="border: 1px solid black;">{d['Destination']}</td>
                        <td style="border: 1px solid black;">{int(d['Kolli'])}</td>
                        <td style="border: 1px solid black;">Rp {float(d['Harga Satuan']):,.0f}</td>
                        <td style="border: 1px solid black;">{int(d['Berat (kg)'])} Kg</td>
                        <td style="border: 1px solid black;">Rp {total_val:,.0f}</td>
                    </tr>
                </table>
                <br>
                <div style="text-align: right;"><strong>YANG HARUS DI BAYAR: Rp {total_val:,.0f}</strong></div>
                <p style="font-size:14px;"><strong>Terbilang:</strong> <em>{terbilang(total_val)} Rupiah</em></p>
                <br>
                <table style="width:100%; border:none;">
                    <tr>
                        <td style="width:60%; border:none; vertical-align: top;">
                            <strong>TRANSFER TO :</strong><br>Bank Central Asia (BCA)<br>6720422334<br>A/N ADITYA GAMA SAPUTRI<br>
                            <small>NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</small>
                        </td>
                        <td style="text-align: center; border:none; position: relative;">
                            Sincerely,<br>PT. GAMA GEMAH GEMILANG<br>
                            <img src="data:image/png;base64,{stempel}" style="width:230px; margin-top:10px;">
                            <img src="data:image/png;base64,{ttd}" style="width:120px; position: absolute; top: 70px; left: 50%; transform: translateX(-50%);">
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

