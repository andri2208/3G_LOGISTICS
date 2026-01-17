import streamlit as st
import pandas as pd
import base64
import os

# =========================================================
# 1. KONFIGURASI HALAMAN & FUNGSI UTAMA
# =========================================================
st.set_page_config(page_title="3G Logistics System", layout="wide")

def get_image_base64(path):
    """Fungsi untuk membaca gambar agar bisa muncul di dalam HTML"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Fungsi untuk mengubah angka menjadi teks terbilang"""
    bilangan = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bilangan[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return "Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return "Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    return "Angka Terlalu Besar"

# =========================================================
# 2. SOURCE DATA (Sesuaikan dengan Google Sheets Anda)
# =========================================================
def fetch_data():
    # Ini adalah contoh data. Jika Anda pakai Google Sheets, 
    # ganti bagian ini dengan kode koneksi sheet Anda.
    data = {
        'Resi': ['REG-001', 'REG-002'],
        'Tanggal': ['29-Des-25', '18-Jan-26'],
        'Pengirim': ['BAPAK ANDI', 'ADE'],
        'Produk': ['SATU SET ALAT TAMBANG', 'PAKET SPAREPART'],
        'Origin': ['SBY', 'SBY'],
        'Destination': ['MEDAN', 'JKT'],
        'Kolli': [10, 5],
        'Harga': [8500, 5000],
        'Berat': [290, 100]
    }
    return pd.DataFrame(data)

# =========================================================
# 3. INTERFACE UTAMA
# =========================================================
st.title("🚚 3G LOGISTICS - INVOICE SYSTEM")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Input Data", "🖨️ Cetak Invoice"])

with tab1:
    st.subheader("Data Pengiriman")
    df = fetch_data()
    st.dataframe(df, use_container_width=True)

with tab2:
    st.info("Halaman Input Data...")

# =========================================================
# 4. LOGIK CETAK INVOICE (TAB 3)
# =========================================================
with tab3:
    st.subheader("Preview Invoice")
    df_inv = fetch_data()
    
    if not df_inv.empty:
        # Dropdown Pilih Resi
        pilih_resi = st.selectbox("Pilih Nomor Resi", df_inv['Resi'].unique())
        
        # Filter Data Berdasarkan Resi
        d = df_inv[df_inv['Resi'] == pilih_resi].iloc[0]
        
        # Hitung Total
        harga = float(d['Harga'])
        berat = float(d['Berat'])
        total_bayar = harga * berat

        # Load Gambar ke Base64
        logo_base = get_image_base64("3G.png")
        ttd_base = get_image_base64("TANDA TANGAN.png")
        stempel_base = get_image_base64("STEMPEL DAN NAMA.png")

        # STRUKTUR HTML INVOICE
        html_content = f"""
        <div style="background-color: white; color: black; padding: 30px; border: 1px solid #ddd; font-family: Arial; width: 850px; margin: auto;">
            <table style="width: 100%; border: none;">
                <tr>
                    <td style="width: 150px;"><img src="data:image/png;base64,{logo_base}" width="130"></td>
                    <td style="vertical-align: middle;">
                        <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:0;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>Telp 031-79973432</p>
                    </td>
                    <td style="text-align:right; vertical-align: top;">
                        <h1 style="margin:0; color:red; font-size: 35px;">INVOICE</h1>
                        <p style="margin:0;"><b>DATE: {d['Tanggal']}</b></p>
                    </td>
                </tr>
            </table>

            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p style="font-size: 16px;"><b>CUSTOMER: {str(d['Pengirim']).upper()}</b></p>

            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid black; text-align: center;">
                <tr style="background-color: #f2f2f2; font-size: 12px;">
                    <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1px solid black;">Product Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">KOLLI</th>
                    <th style="border: 1px solid black;">HARGA</th>
                    <th style="border: 1px solid black;">WEIGHT</th>
                    <th style="border: 1px solid black;">TOTAL</th>
                </tr>
                <tr style="font-size: 13px;">
                    <td style="border: 1px solid black; padding: 20px;">{d['Tanggal']}</td>
                    <td style="border: 1px solid black; text-align: left; padding-left: 10px;">{d['Produk']}</td>
                    <td style="border: 1px solid black;">{d['Origin']}</td>
                    <td style="border: 1px solid black;">{d['Destination']}</td>
                    <td style="border: 1px solid black;">{d['Kolli']}</td>
                    <td style="border: 1px solid black;">Rp {harga:,.0f}</td>
                    <td style="border: 1px solid black;">{berat} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total_bayar:,.0f}</td>
                </tr>
            </table>

            <div style="text-align: right; margin-top: 20px;">
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color:red;">Rp {total_bayar:,.0f}</span></h3>
                <p style="font-size: 13px;"><i>Terbilang: {terbilang(total_bayar)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 40px;">
                <tr>
                    <td style="width: 60%; font-size: 12px; vertical-align: top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia (BCA)<br>
                        No Rek: 6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br><br>
                        <small>NB: Mohon konfirmasi ke Finance 082179799200</small>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="position: relative; height: 120px; width: 180px; margin: auto;">
                            <img src="data:image/png;base64,{ttd_base}" 
                                 style="position: absolute; width: 100px; left: 40px; top: 10px; z-index: 1;">
                            <img src="data:image/png;base64,{stempel_base}" 
                                 style="position: absolute; width: 150px; left: 15px; top: -10px; z-index: 2; opacity: 0.8;">
                        </div>

                        <br><b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # MENAMPILKAN HTML KE STREAMLIT
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Tombol Download
        st.download_button("Download Invoice (HTML)", data=html_content, file_name=f"Invoice_{pilih_resi}.html", mime="text/html")
    else:
        st.error("Data tidak ditemukan.")
