import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI PENDUKUNG (UTILITIES) ---
def get_image_base64(path):
    """Mengonversi gambar lokal ke base64 agar bisa tampil di browser"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Fungsi otomatis untuk mengubah angka menjadi teks rupiah"""
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

# --- 3. DATABASE DALAM APLIKASI (SESSION STATE) ---
# Ini menjaga agar data yang diinput tidak hilang saat pindah tab
if 'db_invoice' not in st.session_state:
    st.session_state.db_invoice = pd.DataFrame(columns=[
        'No_Resi', 'Tanggal', 'Customer', 'Deskripsi', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'
    ])

# --- 4. NAVIGASI ANTARMUKA ---
st.title("🚚 3G LOGISTICS - SYSTEM V3.0")
tab_input, tab_cetak = st.tabs(["📝 INPUT DATA BARU", "🖨️ CETAK INVOICE"])

# --- TAB 1: INPUT DATA ---
with tab_input:
    st.subheader("Form Entry Pengiriman")
    with st.form("form_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            no_resi = st.text_input("Nomor Resi / Invoice", placeholder="Contoh: INV/29/12/25")
            tgl = st.date_input("Tanggal Muat", value=datetime.now())
            customer = st.text_input("Nama Customer", placeholder="BAPAK ANDI")
            barang = st.text_area("Deskripsi Barang", placeholder="SATU SET ALAT TAMBANG")
        
        with col2:
            asal = st.text_input("Origin (Asal)", value="SBY")
            tujuan = st.text_input("Destination (Tujuan)", value="MEDAN")
            koli = st.number_input("Jumlah Kolli", min_value=1, step=1)
            hrga = st.number_input("Harga Satuan (Rp)", min_value=0, step=100)
            brt = st.number_input("Berat Total (Kg)", min_value=0.0, step=0.1)
        
        simpan = st.form_submit_button("SIMPAN DATA ✅")
        
        if simpan:
            if no_resi and customer:
                new_data = pd.DataFrame([{
                    'No_Resi': no_resi,
                    'Tanggal': tgl.strftime('%d-%b-%y'),
                    'Customer': customer.upper(),
                    'Deskripsi': barang.upper(),
                    'Origin': asal.upper(),
                    'Destination': tujuan.upper(),
                    'Kolli': koli,
                    'Harga': hrga,
                    'Berat': brt
                }])
                st.session_state.db_invoice = pd.concat([st.session_state.db_invoice, new_data], ignore_index=True)
                st.success(f"Data {no_resi} Berhasil Disimpan!")
            else:
                st.error("Gagal! Nomor Resi dan Customer wajib diisi.")

# --- TAB 2: CETAK INVOICE ---
with tab_cetak:
    if st.session_state.db_invoice.empty:
        st.warning("Belum ada data. Silakan isi form di Tab Input terlebih dahulu.")
    else:
        st.subheader("Preview Invoice")
        pilihan = st.selectbox("Pilih Nomor Resi", st.session_state.db_invoice['No_Resi'].unique())
        
        # Ambil data dari database berdasarkan pilihan
        d = st.session_state.db_invoice[st.session_state.db_invoice['No_Resi'] == pilihan].iloc[0]
        total_harga = d['Harga'] * d['Berat']
        
        # Load Gambar (PASTIKAN NAMA FILE SAMA DENGAN DI GITHUB)
        header_base64 = get_image_base64("HEADER-INVOCE.PNG")
        ttd_stempel_base64 = get_image_base64("STEMPEL-TANDA-TANGAN.PNG")

        # STRUKTUR DESAIN INVOICE (HTML & CSS)
        invoice_html = f"""
        <div style="background-color: white; color: black; padding: 25px; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            
            <div style="width: 100%; text-align: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{header_base64}" style="width: 100%;">
            </div>

            <div style="text-align: right; margin-bottom: 20px;">
                <h1 style="color: red; margin: 0; font-size: 32px; font-weight: bold;">INVOICE</h1>
                <p style="margin: 0; font-size: 14px;"><b>DATE: {d['Tanggal']}</b></p>
            </div>

            <p style="font-size: 16px; margin-bottom: 10px;"><b>CUSTOMER: {d['Customer']}</b></p>

            <table style="width: 100%; border-collapse: collapse; border: 1.5px solid black; text-align: center; font-size: 12px;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                        <th style="border: 1px solid black; width: 30%;">Product Description</th>
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
                        <td style="border: 1px solid black; padding: 15px;">{d['Tanggal']}</td>
                        <td style="border: 1px solid black; text-align: left; padding-left: 5px;">{d['Deskripsi']}</td>
                        <td style="border: 1px solid black;">{d['Origin']}</td>
                        <td style="border: 1px solid black;">{d['Destination']}</td>
                        <td style="border: 1px solid black;">{d['Kolli']}</td>
                        <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                        <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                        <td style="border: 1px solid black; font-weight: bold;">Rp {total_harga:,.0f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="text-align: right; margin-top: 25px;">
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color: red; font-size: 24px;">Rp {total_harga:,.0f}</span></h3>
                <p style="font-size: 14px; margin-top: 5px;"><i>Terbilang: {terbilang(total_harga)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 40px; font-size: 13px;">
                <tr>
                    <td style="width: 60%; vertical-align: top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia (BCA)<br>
                        No Rek: 6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br><br>
                        <small style="color: grey;">NB: Mohon konfirmasi ke Finance 082179799200</small>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="margin-top: 10px;">
                            <img src="data:image/png;base64,{ttd_stempel_base64}" width="180">
                        </div>

                        <b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # MENAMPILKAN HTML KE STREAMLIT (KUNCI AGAR TIDAK MUNCUL KODE)
        st.markdown(invoice_html, unsafe_allow_html=True)
