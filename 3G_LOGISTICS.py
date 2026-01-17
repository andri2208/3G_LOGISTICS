import streamlit as st
import pandas as pd
import base64
import os

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

# --- 2. FUNGSI UTAMA (GAMBAR & TERBILANG) ---
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
    return str(n)

# --- 3. DATABASE SEMENTARA (Session State) ---
if 'db_logistic' not in st.session_state:
    st.session_state.db_logistic = pd.DataFrame(columns=[
        'Resi', 'Tanggal', 'Pengirim', 'Produk', 'Origin', 'Destination', 'Kolli', 'Harga', 'Berat'
    ])

# --- 4. TAMPILAN TAB ---
st.title("🚚 3G LOGISTICS - INTERNAL SYSTEM")
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Input Data Baru", "🖨️ Cetak Invoice"])

# --- TAB 1: DASHBOARD ---
with tab1:
    st.subheader("Data Pengiriman Terdaftar")
    if st.session_state.db_logistic.empty:
        st.info("Belum ada data. Silakan input di Tab 'Input Data Baru'")
    else:
        st.dataframe(st.session_state.db_logistic, use_container_width=True)

# --- TAB 2: HALAMAN INPUT (DARI NOL) ---
with tab2:
    st.subheader("Form Input Pengiriman Baru")
    with st.form("form_input", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            no_resi = st.text_input("Nomor Resi / Invoice", placeholder="Contoh: INV/2026/001")
            tgl = st.date_input("Tanggal Load")
            pengirim = st.text_input("Nama Customer (Pengirim)")
            produk = st.text_area("Deskripsi Barang", placeholder="Contoh: SATU SET ALAT TAMBANG")
        
        with col2:
            asal = st.text_input("Origin (Asal)", placeholder="Contoh: SBY")
            tujuan = st.text_input("Destination (Tujuan)", placeholder="Contoh: MEDAN")
            kolli = st.number_input("Jumlah Kolli", min_value=1, step=1)
            harga_satuan = st.number_input("Harga per Kg (Rp)", min_value=0, step=100)
            berat_total = st.number_input("Berat Total (Kg)", min_value=0.0, step=0.1)
        
        submit = st.form_submit_button("Simpan Data ✅")
        
        if submit:
            if no_resi and pengirim:
                new_data = pd.DataFrame([{
                    'Resi': no_resi,
                    'Tanggal': tgl.strftime('%d-%b-%y'),
                    'Pengirim': pengirim,
                    'Produk': produk,
                    'Origin': asal,
                    'Destination': tujuan,
                    'Kolli': kolli,
                    'Harga': harga_satuan,
                    'Berat': berat_total
                }])
                st.session_state.db_logistic = pd.concat([st.session_state.db_logistic, new_data], ignore_index=True)
                st.success("Data Berhasil Disimpan! Silakan cek di Tab Cetak Invoice.")
            else:
                st.error("Gagal! Nomor Resi dan Nama Pengirim wajib diisi.")

# --- TAB 3: HALAMAN CETAK ---
with tab3:
    st.subheader("Preview & Cetak Invoice")
    if st.session_state.db_logistic.empty:
        st.warning("Data kosong. Silakan isi form di Tab Input terlebih dahulu.")
    else:
        pilih = st.selectbox("Pilih Resi untuk Dicetak", st.session_state.db_logistic['Resi'].unique())
        d = st.session_state.db_logistic[st.session_state.db_logistic['Resi'] == pilih].iloc[0]
        
        total_bayar = d['Harga'] * d['Berat']
        
        # Load Gambar
        logo = get_image_base64("3G.png")
        ttd = get_image_base64("TANDA TANGAN.png")
        stempel = get_image_base64("STEMPEL DAN NAMA.png")

        # HTML INVOICE
        invoice_html = f"""
        <div style="background: white; color: black; padding: 30px; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            <table style="width: 100%;">
                <tr>
                    <td><img src="data:image/png;base64,{logo}" width="120"></td>
                    <td style="text-align: right; vertical-align: top;">
                        <h1 style="color: red; margin: 0;">INVOICE</h1>
                        <p><b>DATE: {d['Tanggal']}</b></p>
                    </td>
                </tr>
            </table>
            <hr style="border: 2px solid #1a3d8d;">
            <p><b>CUSTOMER: {str(d['Pengirim']).upper()}</b></p>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 13px;">
                <tr style="background: #eee;">
                    <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1px solid black;">Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">Price</th>
                    <th style="border: 1px solid black;">Weight</th>
                    <th style="border: 1px solid black;">Total</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 15px;">{d['Tanggal']}</td>
                    <td style="border: 1px solid black; text-align: left; padding-left: 5px;">{d['Produk']}</td>
                    <td style="border: 1px solid black;">{d['Origin']}</td>
                    <td style="border: 1px solid black;">{d['Destination']}</td>
                    <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                    <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                    <td style="border: 1px solid black;"><b>Rp {total_bayar:,.0f}</b></td>
                </tr>
            </table>
            <div style="text-align: right; margin-top: 20px;">
                <p>Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b></p>
                <div style="position: relative; height: 100px; width: 180px; margin-left: auto;">
                    <img src="data:image/png;base64,{ttd}" style="position: absolute; width: 90px; right: 40px; top: 10px; z-index: 1;">
                    <img src="data:image/png;base64,{stempel}" style="position: absolute; width: 140px; right: 10px; top: 0px; z-index: 2; opacity: 0.8;">
                </div>
                <div style="clear: both; margin-top: 20px;">
                    <b>KELVINITO JAYADI</b><br>DIREKTUR
                </div>
            </div>
        </div>
        """
        st.markdown(invoice_html, unsafe_allow_html=True)
