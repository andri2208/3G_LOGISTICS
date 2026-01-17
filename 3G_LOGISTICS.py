import streamlit as st
import pandas as pd
import base64
import os

# Konfigurasi Halaman
st.set_page_config(page_title="3G LOGISTICS SYSTEM", layout="wide")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Database Sementara
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Resi', 'Tgl', 'Cust', 'Produk', 'Asal', 'Tujuan', 'Hrg', 'Brt'])

tab1, tab2 = st.tabs(["📝 Input Data", "🖨️ Cetak Invoice"])

with tab1:
    st.subheader("Form Input Pengiriman")
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            resi = st.text_input("No Resi", value="INV/2025/001")
            tgl = st.text_input("Tanggal", value="29-Des-25")
            cust = st.text_input("Customer", value="BAPAK ANDI")
            item = st.text_area("Deskripsi Barang", value="SATU SET ALAT TAMBANG")
        with col2:
            asal = st.text_input("Origin", value="SBY")
            tuju = st.text_input("Destination", value="MEDAN")
            hrg = st.number_input("Harga Satuan (Rp)", value=8500)
            brt = st.number_input("Berat (Kg)", value=290.0)
        
        if st.form_submit_button("Simpan Data"):
            new_data = pd.DataFrame([{'Resi':resi, 'Tgl':tgl, 'Cust':cust, 'Produk':item, 'Asal':asal, 'Tujuan':tuju, 'Hrg':hrg, 'Brt':brt}])
            st.session_state.db = pd.concat([st.session_state.db, new_data], ignore_index=True)
            st.success("Data Berhasil Disimpan!")

with tab2:
    if st.session_state.db.empty:
        st.warning("Silakan input data terlebih dahulu.")
    else:
        pilih = st.selectbox("Pilih No Resi", st.session_state.db['Resi'].unique())
        d = st.session_state.db[st.session_state.db['Resi'] == pilih].iloc[0]
        total = d['Hrg'] * d['Brt']
        
        # Load Aset Gambar
        logo = get_image_base64("3G.png")
        ttd = get_image_base64("TANDA TANGAN.png")
        stempel = get_image_base64("STEMPEL DAN NAMA.png")

        # Layout HTML (Render Sempurna)
        invoice_html = f"""
        <div style="background: white; color: black; padding: 40px; border: 1px solid #ddd; font-family: Arial; width: 800px; margin: auto;">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 140px;"><img src="data:image/png;base64,{logo}" width="130"></td>
                    <td>
                        <h2 style="margin:0; color:#1a3d8d;">PT. GAMA GEMAH GEMILANG</h2>
                        <p style="font-size:11px; margin:0;">Ruko Paragon Plaza Blok D-6 Jalan Ngasinan, Kepatihan, Menganti, Gresik.<br>Telp 031-79973432</p>
                    </td>
                    <td style="text-align:right; vertical-align:top;">
                        <h1 style="margin:0; color:red;">INVOICE</h1>
                        <p><b>DATE: {d['Tgl']}</b></p>
                    </td>
                </tr>
            </table>
            <hr style="border: 2px solid #1a3d8d; margin: 20px 0;">
            <p><b>CUSTOMER: {str(d['Cust']).upper()}</b></p>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 12px;">
                <tr style="background: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 10px;">Date of Load</th>
                    <th style="border: 1px solid black;">Product Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">HARGA</th>
                    <th style="border: 1px solid black;">WEIGHT</th>
                    <th style="border: 1px solid black;">TOTAL</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 15px;">{d['Tgl']}</td>
                    <td style="border: 1px solid black; text-align: left; padding-left: 10px;">{d['Produk']}</td>
                    <td style="border: 1px solid black;">{d['Asal']}</td>
                    <td style="border: 1px solid black;">{d['Tujuan']}</td>
                    <td style="border: 1px solid black;">Rp {d['Hrg']:,}</td>
                    <td style="border: 1px solid black;">{d['Brt']} Kg</td>
                    <td style="border: 1px solid black; font-weight: bold;">Rp {total:,.0f}</td>
                </tr>
            </table>
            <div style="text-align: right; margin-top: 25px;">
                <h3 style="margin:0;">YANG HARUS DI BAYAR: <span style="color:red;">Rp {total:,.0f}</span></h3>
            </div>
            <table style="width: 100%; margin-top: 40px;">
                <tr>
                    <td style="width: 60%; vertical-align: top; font-size: 12px;">
                        <b>TRANSFER TO :</b><br>Bank BCA | No Rek: 6720422334<br>A/N ADITYA GAMA SAPUTRI [cite: 13, 14, 15]
                    </td>
                    <td style="text-align: center;">
                        Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b><br>
                        <div style="position: relative; height: 100px; width: 180px; margin: auto;">
                            <img src="data:image/png;base64,{ttd}" style="position: absolute; width: 80px; left: 50px; top: 15px; z-index: 1;">
                            <img src="data:image/png;base64,{stempel}" style="position: absolute; width: 140px; left: 20px; top: -5px; z-index: 2; opacity: 0.85;">
                        </div>
                        <br><b>KELVINITO JAYADI</b><br>DIREKTUR 
                    </td>
                </tr>
            </table>
        </div>
        """
        # Perintah ini yang merubah kode berantakan menjadi desain rapi
        st.markdown(invoice_html, unsafe_allow_html=True)
