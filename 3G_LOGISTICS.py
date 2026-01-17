import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI LOAD GAMBAR ---
def get_image_base64(path):
    """Fungsi untuk memproses gambar agar bisa tampil di web"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. FUNGSI TERBILANG OTOMATIS ---
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

# --- 4. PENYIMPANAN DATA (SESSION STATE) ---
if 'data_inv' not in st.session_state:
    st.session_state.data_inv = pd.DataFrame(columns=[
        'Resi', 'Tanggal', 'Customer', 'Deskripsi', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'
    ])

# --- 5. TAMPILAN TAB ---
st.title("🚚 3G LOGISTICS - INVOICE GENERATOR")
tab1, tab2 = st.tabs(["📝 INPUT DATA BARU", "🖨️ CETAK INVOICE"])

# --- TAB 1: INPUT ---
with tab1:
    st.subheader("Masukkan Detail Pengiriman")
    with st.form("form_input", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            no_resi = st.text_input("Nomor Resi", value="INV/2026/001")
            tgl_muat = st.date_input("Tanggal Muat", value=datetime.now())
            nama_cust = st.text_input("Nama Customer", placeholder="Contoh: BAPAK ANDI")
            barang = st.text_area("Deskripsi Barang", placeholder="Contoh: SATU SET ALAT TAMBANG")
        with c2:
            asal = st.text_input("Origin", value="SBY")
            tujuan = st.text_input("Destination", value="MEDAN")
            koli = st.number_input("KOLLI", min_value=1, step=1)
            price = st.number_input("Harga Satuan (Rp)", min_value=0)
            weight = st.number_input("Weight (Kg)", min_value=0.0)
        
        if st.form_submit_button("SIMPAN DATA ✅"):
            new_row = pd.DataFrame([{
                'Resi': no_resi, 'Tanggal': tgl_muat.strftime('%d-%b-%y'),
                'Customer': nama_cust.upper(), 'Deskripsi': barang.upper(),
                'Origin': asal.upper(), 'Destination': tujuan.upper(),
                'Kolli': koli, 'Harga': price, 'Berat': weight
            }])
            st.session_state.data_inv = pd.concat([st.session_state.data_inv, new_row], ignore_index=True)
            st.success("Data berhasil disimpan! Pindah ke Tab 'CETAK INVOICE'.")

# --- TAB 2: CETAK ---
with tab2:
    if st.session_state.data_inv.empty:
        st.warning("Belum ada data. Silakan input di Tab 1.")
    else:
        resi_pilih = st.selectbox("Pilih No Resi", st.session_state.data_inv['Resi'].unique())
        d = st.session_state.data_inv[st.session_state.data_inv['Resi'] == resi_pilih].iloc[0]
        total_tagihan = d['Harga'] * d['Berat']

        # LOAD GAMBAR (Pastikan nama file di GitHub Anda sama persis)
        header_b64 = get_image_base64("HEADER-INVOCE.PNG")
        ttd_stempel_b64 = get_image_base64("STEMPEL-TANDA-TANGAN.PNG")

        # HTML DESIGN
        invoice_html = f"""
        <div style="background-color: white; color: black; padding: 0; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            
            <img src="data:image/png;base64,{header_b64}" style="width: 100%;">

            <div style="padding: 20px;">
                <div style="text-align: right;">
                    <h1 style="color: red; margin: 0; font-size: 35px;">INVOICE</h1>
                    <p style="margin: 0;"><b>DATE: {d['Tanggal']}</b></p>
                </div>

                <p style="font-size: 16px; margin-top: 10px;"><b>CUSTOMER: {d['Customer']}</b></p>

                <table style="width: 100%; border-collapse: collapse; border: 1.5px solid black; text-align: center; font-size: 12px; margin-top: 10px;">
                    <thead style="background-color: #f2f2f2;">
                        <tr>
                            <th style="border: 1px solid black; padding: 8px;">Date of Load</th>
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
                            <td style="border: 1px solid black; padding: 10px;">{d['Tanggal']}</td>
                            <td style="border: 1px solid black; text-align: left; padding-left: 5px;">{d['Deskripsi']}</td>
                            <td style="border: 1px solid black;">{d['Origin']}</td>
                            <td style="border: 1px solid black;">{d['Destination']}</td>
                            <td style="border: 1px solid black;">{d['Kolli']}</td>
                            <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                            <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                            <td style="border: 1px solid black; font-weight: bold;">Rp {total_tagihan:,.0f}</td>
                        </tr>
                    </tbody>
                </table>

                <div style="text-align: right; margin-top: 20px;">
                    <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color: red; font-size: 22px;">Rp {total_tagihan:,.0f}</span></h3>
                    <p style="font-size: 13px; margin-top: 5px;"><i>Terbilang: {terbilang(total_tagihan)} Rupiah</i></p>
                </div>

                <table style="width: 100%; margin-top: 30px; font-size: 13px;">
                    <tr>
                        <td style="width: 60%; vertical-align: top;">
                            <b>TRANSFER TO :</b><br>
                            Bank Central Asia (BCA)<br>
                            6720422334<br>
                            A/N ADITYA GAMA SAPUTRI<br><br>
                            <small>NB: Mohon konfirmasi ke Finance 082179799200</small>
                        </td>
                        <td style="text-align: center;">
                            Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                            <img src="data:image/png;base64,{ttd_stempel_b64}" width="180"><br>
                            <b>KELVINITO JAYADI</b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        """
        
        # BARIS PENTING: Render HTML
        st.markdown(invoice_html, unsafe_allow_html=True)
