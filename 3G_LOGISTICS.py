import streamlit as st
import pandas as pd
import base64
import os
from datetime import datetime

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI PENDUKUNG ---
def get_image_base64(path):
    """Membaca gambar agar bisa muncul di Streamlit Cloud"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def terbilang(n):
    """Fungsi otomatis mengubah angka menjadi teks (Dua juta...)"""
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

# --- 3. DATABASE SEMENTARA (SESSION STATE) ---
if 'data_logistik' not in st.session_state:
    st.session_state.data_logistik = pd.DataFrame(columns=[
        'No_Resi', 'Tanggal', 'Customer', 'Deskripsi', 'Origin', 'Destination', 'Kolli', 'Harga', 'Weight'
    ])

# --- 4. NAVIGASI TAB ---
st.title("🚚 3G LOGISTICS - INTERNAL DASHBOARD")
tab_input, tab_cetak = st.tabs(["📝 INPUT DATA BARU", "🖨️ CETAK INVOICE"])

# --- TAB 1: INPUT DATA ---
with tab_input:
    st.subheader("Form Input Pengiriman")
    with st.form("form_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            no_resi = st.text_input("Nomor Resi / Invoice", placeholder="Contoh: INV/29/12/25")
            tgl_load = st.date_input("Tanggal Muat (Date of Load)")
            customer = st.text_input("Nama Customer", placeholder="Contoh: BAPAK ANDI")
            barang = st.text_area("Product Description", placeholder="Contoh: SATU SET ALAT TAMBANG")
        
        with col2:
            asal = st.text_input("Origin (Asal)", placeholder="Contoh: SBY")
            tujuan = st.text_input("Destination (Tujuan)", placeholder="Contoh: MEDAN")
            kolli = st.number_input("Jumlah KOLLI", min_value=1, step=1)
            harga = st.number_input("Harga Satuan (Rp)", min_value=0, step=100)
            berat = st.number_input("Weight (Kg)", min_value=0.0, step=0.1)
        
        submit = st.form_submit_button("Simpan Data ke Sistem ✅")
        
        if submit:
            if no_resi and customer:
                # Simpan data ke session state
                data_baru = pd.DataFrame([{
                    'No_Resi': no_resi,
                    'Tanggal': tgl_load.strftime('%d-%b-%y'),
                    'Customer': customer.upper(),
                    'Deskripsi': barang.upper(),
                    'Origin': asal.upper(),
                    'Destination': tujuan.upper(),
                    'Kolli': kolli,
                    'Harga': harga,
                    'Weight': berat
                }])
                st.session_state.data_logistik = pd.concat([st.session_state.data_logistik, data_baru], ignore_index=True)
                st.success(f"Data {no_resi} berhasil disimpan! Buka Tab 'Cetak Invoice' untuk melihat.")
            else:
                st.error("Mohon isi Nomor Resi dan Nama Customer.")

# --- TAB 2: CETAK INVOICE ---
with tab_cetak:
    if st.session_state.data_logistik.empty:
        st.warning("Data masih kosong. Silakan input data di Tab 1.")
    else:
        st.subheader("Preview Invoice")
        resi_pilihan = st.selectbox("Pilih Resi yang akan Dicetak", st.session_state.data_logistik['No_Resi'].unique())
        
        # Ambil detail data yang dipilih
        d = st.session_state.data_logistik[st.session_state.data_logistik['No_Resi'] == resi_pilihan].iloc[0]
        total_bayar = d['Harga'] * d['Weight']

        # Load Gambar (PASTIKAN FILE INI SUDAH DI UPLOAD)
        logo = get_image_base64("3G.png")
        ttd = get_image_base64("TANDA TANGAN.png")
        stempel = get_image_base64("STEMPEL DAN NAMA.png")

        # STRUKTUR HTML (PERSIS PDF)
        invoice_html = f"""
        <div style="background-color: white; color: black; padding: 40px; border: 1px solid #ddd; font-family: Arial, sans-serif; width: 850px; margin: auto;">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 130px;"><img src="data:image/png;base64,{logo}" width="120"></td>
                    <td style="vertical-align: middle;">
                        <h2 style="margin:0; color:#1a3d8d; font-size: 24px;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:0; line-height: 1.2;">
                            Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>
                            Jawa Timur. Telp 031-79973432
                        </p>
                    </td>
                    <td style="text-align:right; vertical-align: top;">
                        <h1 style="margin:0; color:red; font-size: 32px;">INVOICE</h1>
                        <p style="margin:0;"><b>DATE: {d['Tanggal']}</b></p>
                    </td>
                </tr>
            </table>

            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p style="font-size: 16px; margin-bottom: 10px;"><b>CUSTOMER: {d['Customer']}</b></p>

            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 12px;">
                <thead style="background-color: #f2f2f2;">
                    <tr>
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
                        <td style="border: 1px solid black; padding: 20px;">{d['Tanggal']}</td>
                        <td style="border: 1px solid black; text-align: left; padding-left: 10px;">{d['Deskripsi']}</td>
                        <td style="border: 1px solid black;">{d['Origin']}</td>
                        <td style="border: 1px solid black;">{d['Destination']}</td>
                        <td style="border: 1px solid black;">{d['Kolli']}</td>
                        <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                        <td style="border: 1px solid black;">{d['Weight']} Kg</td>
                        <td style="border: 1px solid black; font-weight: bold;">Rp {total_bayar:,.0f}</td>
                    </tr>
                </tbody>
            </table>

            <div style="text-align: right; margin-top: 25px;">
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color:red; font-size: 22px;">Rp {total_bayar:,.0f}</span></h3>
                <p style="font-size: 14px; margin-top: 5px;"><i>Terbilang: {terbilang(total_bayar)} Rupiah</i></p>
            </div>

            <table style="width: 100%; margin-top: 40px; font-size: 13px;">
                <tr>
                    <td style="width: 60%; vertical-align: top;">
                        <b>TRANSFER TO :</b><br>
                        Bank Central Asia (BCA)<br>
                        6720422334<br>
                        A/N ADITYA GAMA SAPUTRI<br><br>
                        <small style="color: grey;">NB: Jika sudah transfer mohon konfirmasi ke Finance 082179799200</small>
                    </td>
                    <td style="text-align: center; vertical-align: top;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        
                        <div style="position: relative; height: 120px; width: 200px; margin: auto;">
                            <img src="data:image/png;base64,{ttd}" 
                                 style="position: absolute; width: 100px; left: 50px; top: 15px; z-index: 1;">
                            
                            <img src="data:image/png;base64,{stempel}" 
                                 style="position: absolute; width: 150px; left: 25px; top: -5px; z-index: 2; opacity: 0.85;">
                        </div>

                        <br><b>KELVINITO JAYADI</b><br>DIREKTUR
                    </td>
                </tr>
            </table>
        </div>
        """
        
        # MENAMPILKAN HASILNYA
        st.markdown(invoice_html, unsafe_allow_html=True)
