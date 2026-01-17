import streamlit as st
import pandas as pd
import base64
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G Logistics - System", layout="wide")

# --- 2. FUNGSI PEMBANTU (UTILITIES) ---
def get_image_base64(path):
    """Mengubah gambar lokal menjadi format base64 agar bisa tampil di HTML"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Fungsi sederhana untuk mengubah angka menjadi teks (terbilang)"""
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12:
        return bilangan[int(n)]
    elif n < 20:
        return terbilang(n - 10) + " Belas"
    elif n < 100:
        return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200:
        return "Seratus " + terbilang(n - 100)
    elif n < 1000:
        return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000:
        return "Seribu " + terbilang(n - 1000)
    elif n < 1000000:
        return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return str(n)

# --- 3. SIMULASI DATABASE (Ganti dengan fetch_data Anda yang asli) ---
def fetch_data():
    # Contoh data simulasi jika database kosong
    data = {
        'Resi': ['REG-001', 'REG-002'],
        'Tanggal': ['17-Jan-26', '18-Jan-26'],
        'Pengirim': ['Bapak Andi', 'Ade'],
        'Produk': ['SATU SET ALAT TAMBANG', 'PAKET'],
        'Origin': ['SBY', 'SBY'],
        'Destination': ['MEDAN', 'MEDAN'],
        'Kolli': [10, 40],
        'Harga': ['8500', '8000'],
        'Berat': [290, 140]
    }
    return pd.DataFrame(data)

# --- 4. TAMPILAN UTAMA ---
st.title("🚚 3G LOGISTICS SYSTEM")

tab1, tab2, tab3 = st.tabs(["Dashboard", "Input Data", "Cetak Invoice"])

with tab1:
    st.write("Selamat Datang di Sistem PT. GGG")
    st.dataframe(fetch_data())

with tab2:
    st.write("Fitur Input Data...")

# --- 5. BAGIAN CETAK INVOICE (TAB 3) ---
with tab3:
    st.header("Cetak Invoice")
    df_inv = fetch_data()
    
    if not df_inv.empty and 'Resi' in df_inv.columns:
        # Pilih Resi
        pilih_resi = st.selectbox("Pilih No Resi", df_inv['Resi'].dropna().unique())
        
        # Ambil Data
        d = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
        
        # Perhitungan
        h_raw = str(d.get('Harga', '0')).split('.')[0]
        harga_fix = int("".join(filter(str.isdigit, h_raw))) if any(c.isdigit() for c in h_raw) else 0
        berat_fix = float(pd.to_numeric(d.get('Berat', 0), errors='coerce'))
        total_harga = harga_fix * berat_fix

        # Load Gambar (Base64)
        logo_base = get_image_base64("3G.png")
        ttd_base = get_image_base64("TANDA TANGAN.png")
        stempel_base = get_image_base64("STEMPEL DAN NAMA.png")

        # HTML Structure
        html_invoice = f"""
        <div style="background-color: white; color: black; padding: 40px; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            
            <table style="width: 100%;">
                <tr>
                    <td style="width: 150px;"><img src="data:image/png;base64,{logo_base}" width="130"></td>
                    <td>
                        <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:0;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>Telp 031-79973432</p>
                    </td>
                    <td style="text-align:right; vertical-align:top;">
                        <h1 style="margin:0; color:#d62828;">INVOICE</h1>
                        <p><b>DATE: {d.get('Tanggal','')}</b></p>
                    </td>
                </tr>
            </table>

            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p style="font-size:16px;"><b>CUSTOMER: {str(d.get('Pengirim','')).upper()}</b></p>

            <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; border: 1px solid black;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1px solid black;">Product Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">KOLLI</th>
                    <th style="border: 1px solid black;">HARGA</th>
                    <th style="border: 1px solid black;">WEIGHT</th>
                    <th style="border: 1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 15px;">{d.get('Tanggal','')}</td>
                    <td style="border: 1px solid black; text-align: left; padding: 15px;">{d.get('Produk','')}</td>
                    <td style="border: 1px solid black;">{d.get('Origin','')}</td>
                    <td style="border: 1px solid black;">{d.get('Destination','')}</td>
                    <td style="border: 1px solid black;">{d.get('Kolli',0)}</td>
                    <td style="border: 1px solid black;">Rp {harga_fix:,}</td>
                    <td style="border: 1px solid black;">{berat_fix} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total_harga:,.0f}</td>
                </tr>
            </table>

            <div style="text-align: right; margin-top: 25px;">
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color:#d62828;">Rp {total_harga:,.0f}</span></h3>
                <p style="font-size:14px;"><i>Terbilang: {terbilang(total_harga)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 50px;">
                <tr>
                    <td style="width: 60%; vertical-align: top; font-size: 13px;">
                        <b>TRANSFER TO :</b><br>Bank BCA | No Rek: 6720422334<br>A/N ADITYA GAMA SAPUTRI<br><br>
                        <small>NB: Konfirmasi ke Finance 082179799200</small>
                    </td>
                    <td style="text-align: center; vertical-align: top; font-size: 14px;">
                        Gresik, {d.get('Tanggal','')}<br>Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="position: relative; height: 120px; width: 180px; margin: auto;">
                            <img src="data:image/png;base64,{ttd_base}" 
                                 style="position: absolute; width: 100px; left: 40px; top: 15px; z-index: 1;">
                            
                            <img src="data:image/png;base64,{stempel_base}" 
                                 style="position: absolute; width: 150px; left: 15px; top: -5px; z-index: 2; opacity: 0.85;">
                        </div>

                        <br><b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # Render HTML
        st.markdown(html_invoice, unsafe_allow_html=True)
    else:
        st.warning("Silakan isi data terlebih dahulu di Tab Input.")
