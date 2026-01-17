import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI PENDUKUNG ---
def get_image_base64(path):
    """Mengubah gambar ke format yang bisa dibaca HTML di Streamlit"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Mengubah angka menjadi teks rupiah"""
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

# --- 3. DATABASE DALAM APLIKASI (Session State) ---
if 'data_invoice' not in st.session_state:
    st.session_state.data_invoice = pd.DataFrame(columns=[
        'No_Resi', 'Tanggal', 'Customer', 'Barang', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'
    ])

# --- 4. NAVIGASI HALAMAN ---
st.title("🚚 3G LOGISTICS - MANAGEMENT SYSTEM")
tab_input, tab_cetak = st.tabs(["📝 INPUT DATA BARU", "🖨️ CETAK INVOICE"])

# --- HALAMAN 1: INPUT DATA ---
with tab_input:
    st.subheader("Form Input Pengiriman")
    # Form ini akan mengosongkan diri setelah klik simpan
    with st.form("form_invoice", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            no_resi = st.text_input("Nomor Resi / Invoice", placeholder="Contoh: INV/29/12/25")
            tgl_muat = st.date_input("Tanggal Muat", value=datetime.now())
            nama_cust = st.text_input("Nama Customer", placeholder="BAPAK ANDI")
            nama_barang = st.text_area("Deskripsi Produk", placeholder="SATU SET ALAT TAMBANG")
        
        with col2:
            asal_kota = st.text_input("Origin (Asal)", placeholder="SBY")
            tujuan_kota = st.text_input("Destination (Tujuan)", placeholder="MEDAN")
            jml_kolli = st.number_input("Jumlah KOLLI", min_value=1, step=1)
            harga_satuan = st.number_input("Harga per Kg (Rp)", min_value=0, step=100)
            berat_total = st.number_input("Berat Total (Kg)", min_value=0.0, step=0.1)
        
        submit_btn = st.form_submit_button("Simpan Data ✅")
        
        if submit_btn:
            if no_resi and nama_cust:
                new_row = pd.DataFrame([{
                    'No_Resi': no_resi,
                    'Tanggal': tgl_muat.strftime('%d-%b-%y'),
                    'Customer': nama_cust.upper(),
                    'Barang': nama_barang.upper(),
                    'Origin': asal_kota.upper(),
                    'Destination': tujuan_kota.upper(),
                    'Kolli': jml_kolli,
                    'Harga': harga_satuan,
                    'Berat': berat_total
                }])
                st.session_state.data_invoice = pd.concat([st.session_state.data_invoice, new_row], ignore_index=True)
                st.success(f"Berhasil! Data {no_resi} sudah masuk ke sistem.")
            else:
                st.error("Gagal! Nomor Resi dan Customer wajib diisi.")

# --- HALAMAN 2: CETAK INVOICE (Sesuai PDF) ---
with tab_cetak:
    if st.session_state.data_invoice.empty:
        st.warning("Belum ada data. Silakan input di Tab pertama.")
    else:
        st.subheader("Pratinjau Invoice")
        pilihan_resi = st.selectbox("Pilih No. Resi untuk Dicetak", st.session_state.data_invoice['No_Resi'].unique())
        
        # Ambil data spesifik
        d = st.session_state.data_invoice[st.session_state.data_invoice['No_Resi'] == pilihan_resi].iloc[0]
        total_harga = d['Harga'] * d['Berat']

        # Load Gambar Aset
        logo_base = get_image_base64("3G.png")
        ttd_base = get_image_base64("TANDA TANGAN.png")
        stempel_base = get_image_base64("STEMPEL DAN NAMA.png")

        # HTML DESIGN (Identik dengan PDF)
        invoice_html = f"""
        <div style="background-color: white; color: black; padding: 40px; border: 1px solid #ccc; font-family: Arial; width: 850px; margin: auto;">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 140px;"><img src="data:image/png;base64,{logo_base}" width="130"></td>
                    <td style="vertical-align: middle;">
                        <h2 style="margin:0; color:#1a3d8d; font-size: 22px;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:0;">
                            Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>
                            Jawa Timur. Telp 031-79973432
                        </p>
                    </td>
                    <td style="text-align:right; vertical-align:top;">
                        <h1 style="margin:0; color:red; font-size: 35px;">INVOICE</h1>
                        <p style="margin:0;"><b>DATE: {d['Tanggal']}</b></p>
                    </td>
                </tr>
            </table>

            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p style="font-size: 16px; margin-bottom: 10px;"><b>CUSTOMER: {d['Customer']}</b></p>

            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 12px;">
                <thead>
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
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid black; padding: 15px;">{d['Tanggal']}</td>
                        <td style="border: 1px solid black; text-align: left; padding-left: 10px;">{d['Barang']}</td>
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
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color:red; font-size: 24px;">Rp {total_harga:,.0f}</span></h3>
                <p style="font-size: 13px;"><i>Terbilang: {terbilang(total_harga)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 50px; font-size: 13px;">
                <tr>
                    <td style="width: 60%; vertical-align: top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia (BCA)<br>
                        6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br><br>
                        <small style="color: grey;">NB: Mohon konfirmasi ke Finance 082179799200</small>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="position: relative; height: 110px; width: 180px; margin: auto;">
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
        # Render HTML ke layar
        st.markdown(invoice_html, unsafe_allow_html=True)
