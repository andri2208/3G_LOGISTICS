import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI PENDUKUNG ---
def get_image_base64(path):
    """Membaca gambar agar bisa muncul di dalam kode HTML"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Otomatis mengubah angka total menjadi teks rupiah"""
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

# --- 3. DATASHEET / DATABASE SESSION ---
# Menyiapkan tabel penyimpanan data agar tidak hilang saat pindah tab
if 'dataset_invoice' not in st.session_state:
    st.session_state.dataset_invoice = pd.DataFrame(columns=[
        'No_Resi', 'Tanggal', 'Customer', 'Barang', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'
    ])

# --- 4. HEADER GAMBAR (PENGGANTI TEKS JUDUL) ---
if os.path.exists("FAVICON.png"):
    st.image("FAVICON.png", use_container_width=True)
else:
    st.title("3G LOGISTICS SYSTEM")

# --- 5. NAVIGASI TAB ---
tab_input, tab_cetak = st.tabs(["📝 INPUT DATA BARU", "🖨️ CETAK INVOICE"])

# --- HALAMAN INPUT DATA ---
with tab_input:
    st.subheader("Form Datasheet Pengiriman")
    with st.form("form_data", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            in_resi = st.text_input("Nomor Resi / Invoice", placeholder="Contoh: INV/001/2026")
            in_tgl = st.date_input("Tanggal Muat", value=datetime.now())
            in_cust = st.text_input("Nama Customer", placeholder="Contoh: BAPAK ANDI")
            in_barang = st.text_area("Deskripsi Barang", placeholder="Contoh: SATU SET ALAT TAMBANG")
        
        with col2:
            in_asal = st.text_input("Origin (Asal)", value="SBY")
            in_tujuan = st.text_input("Destination (Tujuan)", value="MEDAN")
            in_kolli = st.number_input("Jumlah Kolli", min_value=1, step=1)
            in_harga = st.number_input("Harga Satuan (Rp)", min_value=0, step=100)
            in_berat = st.number_input("Berat Total (Kg)", min_value=0.0, step=0.1)
        
        simpan = st.form_submit_button("SIMPAN KE DATASHEET ✅")
        
        if simpan:
            if in_resi and in_cust:
                # Menambahkan data ke Dataset
                new_row = pd.DataFrame([{
                    'No_Resi': in_resi,
                    'Tanggal': in_tgl.strftime('%d-%b-%y'),
                    'Customer': in_cust.upper(),
                    'Barang': in_barang.upper(),
                    'Origin': in_asal.upper(),
                    'Destination': in_tujuan.upper(),
                    'Kolli': in_kolli,
                    'Harga': in_harga,
                    'Berat': in_berat
                }])
                st.session_state.dataset_invoice = pd.concat([st.session_state.dataset_invoice, new_row], ignore_index=True)
                st.success(f"Data {in_resi} berhasil disimpan!")
            else:
                st.error("Mohon isi No Resi dan Nama Customer!")

# --- HALAMAN CETAK INVOICE ---
with tab_cetak:
    if st.session_state.dataset_invoice.empty:
        st.warning("Datasheet kosong. Silakan input data terlebih dahulu.")
    else:
        st.subheader("Pilih Data Untuk Dicetak")
        resi_pilihan = st.selectbox("Pilih No. Resi", st.session_state.dataset_invoice['No_Resi'].unique())
        
        # Mengambil baris data berdasarkan pilihan
        d = st.session_state.dataset_invoice[st.session_state.dataset_invoice['No_Resi'] == resi_pilihan].iloc[0]
        total_harga = float(d['Harga']) * float(d['Berat'])
        
        # Load Aset Gambar untuk Invoice
        header_b64 = get_image_base64("HEADER INVOICE.PNG")
        ttd_stempel_b64 = get_image_base64("STEMPEL TANDA TANGAN.PNG")

        # STRUKTUR DESAIN INVOICE HTML
        invoice_html = f"""
        <div style="background-color: white; color: black; padding: 0; border: 1px solid #eee; font-family: Arial; width: 850px; margin: auto;">
            
            <img src="data:image/png;base64,{header_b64}" style="width: 100%;">

            <div style="padding: 30px;">
                <div style="text-align: right; margin-bottom: 10px;">
                    <h1 style="color: red; margin: 0; font-size: 35px; font-weight: bold;">INVOICE</h1>
                    <p style="margin: 0; font-size: 14px;"><b>DATE: {d['Tanggal']}</b></p>
                </div>

                <p style="font-size: 16px; margin-bottom: 15px;"><b>CUSTOMER: {d['Customer']}</b></p>

                <table style="width: 100%; border-collapse: collapse; border: 1.5px solid black; text-align: center; font-size: 12px;">
                    <thead style="background-color: #f2f2f2;">
                        <tr>
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
                            <td style="border: 1px solid black; text-align: left; padding-left: 5px;">{d['Barang']}</td>
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

                <table style="width: 100%; margin-top: 50px; font-size: 13px;">
                    <tr>
                        <td style="width: 55%; vertical-align: top;">
                            <b>TRANSFER TO :</b><br>
                            Bank Central Asia (BCA)<br>
                            No Rek: 6720422334<br>
                            A/N ADITYA GAMA SAPUTRI<br><br>
                            <small style="color: grey;">NB: Mohon konfirmasi ke Finance 082179799200</small>
                        </td>
                        <td style="text-align: center; vertical-align: top;">
                            Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                            <div style="margin-top: 10px; margin-bottom: 10px;">
                                <img src="data:image/png;base64,{ttd_stempel_b64}" width="200">
                            </div>
                            <b>KELVINITO JAYADI</b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        """
        # Render HTML agar tampil sebagai invoice rapi, bukan kode
        st.markdown(invoice_html, unsafe_allow_html=True)
