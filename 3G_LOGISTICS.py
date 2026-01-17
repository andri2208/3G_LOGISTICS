import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="3G LOGISTICS - System",
    page_icon="3G.png",
    layout="wide"
)

# --- 2. FUNGSI TOOLS & GAMBAR ---
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

# Load Asset Gambar
logo_base = get_image_base64("3G.png")
stempel_base = get_image_base64("STEMPEL.png")
ttd_base = get_image_base64("TTD.png")

# --- 3. KONEKSI GOOGLE SHEETS ---
# Pastikan URL sheet sudah benar di secrets atau input manual di sini
url = "https://docs.google.com/spreadsheets/d/1doFjOpOIR6fZ4KngeiG77lzgbql3uwFFoHzq81pxMNk/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    return conn.read(spreadsheet=url, usecols=list(range(9)))

# --- 4. TAMPILAN HEADER DASHBOARD ---
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 20px;">
        <img src="data:image/png;base64,{logo_base}" width="90">
        <div>
            <h1 style="margin: 0; color: #1a3d8d;">PT. GAMA GEMAH GEMILANG</h1>
            <p style="margin: 0; color: #d62828; font-weight: bold;">Management Logistics System</p>
        </div>
    </div>
    <hr style="border-top: 3px solid #1a3d8d;">
    """, unsafe_allow_html=True
)

# --- 5. TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Tambah Data", "📂 Database", "🧾 Cetak Invoice"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal", datetime.now())
            resi = st.text_input("Nomor Resi")
            pengirim = st.text_input("Nama Customer")
            produk = st.text_input("Deskripsi Barang")
        with col2:
            origin = st.text_input("Origin")
            dest = st.text_input("Destination")
            kolli = st.number_input("Kolli", min_value=1)
            harga = st.number_input("Harga Satuan", min_value=0)
            berat = st.number_input("Berat (Kg)", min_value=0.0)
        
        if st.form_submit_button("Simpan ke Google Sheets"):
            # Siapkan data baru
            new_row = pd.DataFrame([{
                "Tanggal": tgl.strftime('%d-%b-%y'),
                "Resi": resi,
                "Pengirim": pengirim,
                "Produk": produk,
                "Origin": origin,
                "Destination": dest,
                "Kolli": kolli,
                "Harga": harga,
                "Berat": berat
            }])
            
            # Ambil data lama, gabung, dan update
            df_existing = fetch_data()
            df_updated = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(spreadsheet=url, data=df_updated)
            st.success("Data Berhasil Terkirim ke Google Sheets!")
            st.rerun()

with tab2:
    st.subheader("Data Logistik Real-time")
    df = fetch_data()
    st.dataframe(df, use_container_width=True)

with tab3:
    # Mengambil data terbaru dari Google Sheets
    df = fetch_data()
    
    if not df.empty:
        # 1. Validasi Kolom (Mencegah KeyError)
        # Menghapus spasi di awal/akhir nama kolom agar lebih aman
        df.columns = df.columns.str.strip()
        
        kolom_tersedia = df.columns.tolist()
        kolom_dibutuhkan = ['Resi', 'Harga', 'Berat', 'Produk', 'Pengirim', 'Tanggal', 'Origin', 'Destination', 'Kolli']
        
        # Cek apakah kolom kunci ada
        if 'Resi' in kolom_tersedia:
            pilih_resi = st.selectbox("Pilih Resi untuk Dicetak", df['Resi'].dropna().unique())
            
            # Filter data berdasarkan resi yang dipilih
            d = df[df['Resi'] == pilih_resi].iloc[0]
            
            # 2. Konversi Angka secara Aman (Mencegah TypeError)
            try:
                # Mengubah ke numeric, jika gagal jadi 0
                val_harga = pd.to_numeric(d.get('Harga', 0), errors='coerce')
                val_berat = pd.to_numeric(d.get('Berat', 0), errors='coerce')
                total_harga = float(val_harga * val_berat)
            except:
                total_harga = 0.0

            # --- TAMPILAN INVOICE ---
            st.markdown(f"""
            <div style="border: 2px solid #ddd; padding: 40px; background: white; color: black; font-family: sans-serif;">
                <table style="width:100%; border:none; border-collapse: collapse;">
                    <tr>
                        <td style="width:15%; border:none; vertical-align: middle;">
                            <img src="data:image/png;base64,{logo_base}" width="100">
                        </td>
                        <td style="border:none; padding-left:20px; vertical-align: middle;">
                            <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                            <p style="margin:2px 0; font-size:12px;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>
                            Telp: 031-79973432 | Email: finance@3glogistics.com</p>
                        </td>
                        <td style="text-align:right; border:none; vertical-align:middle;">
                            <h1 style="margin:0; color:#d62828;">INVOICE</h1>
                            <p style="margin:0; font-weight:bold;"># {d.get('Resi', '-')}</p>
                        </td>
                    </tr>
                </table>
                
                <hr style="border: none; border-top: 3px solid #1a3d8d; margin-top: 15px;">
                
                <table style="width:100%; margin-top:20px; border:none;">
                    <tr>
                        <td style="border:none;"><strong>KEPADA:</strong><br>{str(d.get('Pengirim', 'GENERAL CUSTOMER')).upper()}</td>
                        <td style="text-align:right; border:none;">
                            <strong>TANGGAL:</strong> {d.get('Tanggal', '-')}<br>
                            <strong>STATUS:</strong> PAID
                        </td>
                    </tr>
                </table>

                <table style="width:100%; border-collapse: collapse; margin-top:30px; text-align:center; border: 1px solid #333;">
                    <thead>
                        <tr style="background:#1a3d8d; color:white;">
                            <th style="border:1px solid #333; padding:10px;">ITEM</th>
                            <th style="border:1px solid #333; padding:10px;">ORIGIN</th>
                            <th style="border:1px solid #333; padding:10px;">DEST</th>
                            <th style="border:1px solid #333; padding:10px;">QTY</th>
                            <th style="border:1px solid #333; padding:10px;">BERAT</th>
                            <th style="border:1px solid #333; padding:10px;">HARGA</th>
                            <th style="border:1px solid #333; padding:10px;">TOTAL</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="border:1px solid #333; padding:15px; text-align: left;">{d.get('Produk', '-')}</td>
                            <td style="border:1px solid #333;">{d.get('Origin', '-')}</td>
                            <td style="border:1px solid #333;">{d.get('Destination', '-')}</td>
                            <td style="border:1px solid #333;">{d.get('Kolli', 0)}</td>
                            <td style="border:1px solid #333;">{d.get('Berat', 0)} Kg</td>
                            <td style="border:1px solid #333;">Rp {float(d.get('Harga', 0)):,.0f}</td>
                            <td style="border:1px solid #333; font-weight:bold;">Rp {total_harga:,.0f}</td>
                        </tr>
                    </tbody>
                </table>

                <div style="margin-top:20px; background:#f9f9f9; padding:15px; border-left:5px solid #d62828;">
                    <strong>TERBILANG:</strong> {terbilang(total_harga)} Rupiah
                </div>

                <table style="width:100%; margin-top:50px; border:none;">
                    <tr>
                        <td style="border:none; font-size:12px; vertical-align: top;">
                            <strong>PEMBAYARAN VIA:</strong><br>
                            Bank Central Asia (BCA)<br>
                            No. Rekening: 6720422334<br>
                            A/N: ADITYA GAMA SAPUTRI
                        </td>
                        <td style="text-align:center; border:none;">
                            Gresik, {d.get('Tanggal', '-')}<br>
                            Hormat Kami,<br><br>
                            <div style="position:relative; display:inline-block; height: 100px;">
                                <img src="data:image/png;base64,{stempel_base}" width="140" style="opacity: 0.9;">
                                <img src="data:image/png;base64,{ttd_base}" width="90" style="position:absolute; top:15px; left:25px;">
                            </div>
                            <br><b>PT. GAMA GEMAH GEMILANG</b>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Kolom 'Resi' tidak ditemukan di Google Sheets. Kolom yang ada: {kolom_tersedia}")
    else:
        st.warning("Database kosong. Silakan tambah data terlebih dahulu.")
