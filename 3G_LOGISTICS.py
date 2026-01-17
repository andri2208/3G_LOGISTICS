import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI PENDUKUNG ---
def get_image_base64(path):
    """Membaca gambar agar bisa muncul di dalam desain HTML"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Otomatis merubah angka jadi tulisan rupiah"""
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

# --- 3. DATABASE DALAM APLIKASI ---
if 'db_inv' not in st.session_state:
    st.session_state.db_inv = pd.DataFrame(columns=[
        'No_Resi', 'Tanggal', 'Customer', 'Barang', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'
    ])

# --- 4. TAMPILAN TAB ---
st.title("🚚 3G LOGISTICS - SYSTEM V.2")
tab_input, tab_cetak = st.tabs(["📝 INPUT DATA", "🖨️ CETAK INVOICE"])

# --- TAB 1: INPUT DATA ---
with tab_input:
    st.subheader("Form Entry Data Pengiriman")
    with st.form("form_baru", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            no_resi = st.text_input("Nomor Resi / Invoice", placeholder="Contoh: INV/29/12/25")
            tgl = st.date_input("Tanggal Muat", value=datetime.now())
            cust = st.text_input("Nama Customer", placeholder="Contoh: BAPAK ANDI")
            item = st.text_area("Deskripsi Barang", placeholder="Contoh: SATU SET ALAT TAMBANG")
        with col2:
            asal = st.text_input("Origin (Asal)", value="SBY")
            tuju = st.text_input("Destination (Tujuan)", value="MEDAN")
            koli = st.number_input("Jumlah Kolli", min_value=1, step=1)
            hrga = st.number_input("Harga per Kg (Rp)", min_value=0, step=100)
            brt = st.number_input("Berat Total (Kg)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("SIMPAN DATA ✅"):
            new_data = pd.DataFrame([{
                'No_Resi': no_resi,
                'Tanggal': tgl.strftime('%d-%b-%y'),
                'Customer': cust.upper(),
                'Barang': item.upper(),
                'Origin': asal.upper(),
                'Destination': tuju.upper(),
                'Kolli': koli,
                'Harga': hrga,
                'Berat': brt
            }])
            st.session_state.db_inv = pd.concat([st.session_state.db_inv, new_data], ignore_index=True)
            st.success("Data Berhasil Disimpan!")

# --- TAB 2: CETAK INVOICE ---
with tab_cetak:
    if st.session_state.db_inv.empty:
        st.warning("Belum ada data. Silakan isi form di Tab Input.")
    else:
        resi_pilih = st.selectbox("Pilih No Resi", st.session_state.db_inv['No_Resi'].unique())
        d = st.session_state.db_inv[st.session_state.db_inv['No_Resi'] == resi_pilih].iloc[0]
        total_bayar = d['Harga'] * d['Berat']
        
        # Load Gambar Baru Sesuai Request
        header_img = get_image_base64("HEADER-INVOCE.PNG")
        ttd_stempel_img = get_image_base64("STEMPEL-TANDA-TANGAN.PNG")

        # STRUKTUR HTML INVOICE (DESAIN PDF BAPAK ANDI)
        html_content = f"""
        <div style="background: white; color: black; padding: 20px; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            
            <div style="width: 100%; text-align: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{header_img}" style="width: 100%;">
            </div>

            <div style="text-align: right; margin-right: 20px;">
                <h1 style="color: red; margin: 0; font-size: 30px;">INVOICE</h1>
                <p style="margin: 0;"><b>DATE: {d['Tanggal']}</b></p>
            </div>

            <p style="font-size: 16px; margin-left: 20px;"><b>CUSTOMER: {d['Customer']}</b></p>

            <table style="width: 95%; border-collapse: collapse; border: 1.5px solid black; margin: auto; text-align: center; font-size: 13px;">
                <tr style="background: #f2f2f2;">
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
                    <td style="border: 1px solid black; padding: 15px;">{d['Tanggal']}</td>
                    <td style="border: 1px solid black; text-align: left; padding-left: 5px;">{d['Barang']}</td>
                    <td style="border: 1px solid black;">{d['Origin']}</td>
                    <td style="border: 1px solid black;">{d['Destination']}</td>
                    <td style="border: 1px solid black;">{d['Kolli']}</td>
                    <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                    <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total_bayar:,.0f}</td>
                </tr>
            </table>

            <div style="text-align: right; margin-top: 20px; margin-right: 25px;">
                <h3 style="margin: 0;">YANG HARUS DI BAYAR: <span style="color: red; font-size: 22px;">Rp {total_bayar:,.0f}</span></h3>
                <p style="font-size: 13px; margin-top: 5px;"><i>Terbilang: {terbilang(total_bayar)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 40px; font-size: 13px;">
                <tr>
                    <td style="width: 55%; padding-left: 20px; vertical-align: top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia (BCA)<br>
                        6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br><br>
                        <small style="color: grey;">NB: Mohon konfirmasi ke Finance 082179799200</small>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="margin-top: 10px;">
                            <img src="data:image/png;base64,{ttd_stempel_img}" width="180">
                        </div>

                        <b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # PERINTAH AGAR HTML DITAMPILKAN SEBAGAI DESAIN (BUKAN KODE)
        st.markdown(html_content, unsafe_allow_html=True)
