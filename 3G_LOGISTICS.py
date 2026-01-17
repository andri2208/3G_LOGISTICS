import streamlit as st
import pandas as pd
import base64
import os

# --- 1. KONFIGURASI ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Database session agar data tidak hilang saat klik tombol
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Resi', 'Tgl', 'Cust', 'Produk', 'Asal', 'Tujuan', 'Hrg', 'Brt'])

# --- 2. TAMPILAN TAB ---
tab1, tab2 = st.tabs(["📝 INPUT DATA", "🖨️ CETAK INVOICE"])

with tab1:
    st.subheader("Form Input Pengiriman")
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        with c1:
            resi = st.text_input("No Resi", value="INV/001")
            tgl = st.text_input("Tanggal", value="29-Des-25")
            cust = st.text_input("Customer", value="BAPAK ANDI")
            item = st.text_area("Barang", value="SATU SET ALAT TAMBANG")
        with c2:
            asal = st.text_input("Origin", value="SBY")
            tuju = st.text_input("Destination", value="MEDAN")
            hrg = st.number_input("Harga Satuan", value=8500)
            brt = st.number_input("Berat (Kg)", value=290.0)
        
        if st.form_submit_button("Simpan Data"):
            new_row = pd.DataFrame([{'Resi':resi, 'Tgl':tgl, 'Cust':cust, 'Produk':item, 'Asal':asal, 'Tujuan':tuju, 'Hrg':hrg, 'Brt':brt}])
            st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
            st.success("Data Tersimpan!")

with tab2:
    if st.session_state.db.empty:
        st.warning("Belum ada data.")
    else:
        pilih = st.selectbox("Pilih Resi", st.session_state.db['Resi'].unique())
        d = st.session_state.db[st.session_state.db['Resi'] == pilih].iloc[0]
        total = d['Hrg'] * d['Brt']
        
        # Load Gambar
        logo = get_image_base64("3G.png")
        ttd = get_image_base64("TANDA TANGAN.png")
        stempel = get_image_base64("STEMPEL DAN NAMA.png")

        # --- VARIABEL HTML ---
        html_invoice = f"""
        <div style="background: white; color: black; padding: 30px; border: 1px solid #ddd; font-family: Arial; width: 750px; margin: auto;">
            <table style="width: 100%;">
                <tr>
                    <td><img src="data:image/png;base64,{logo}" width="120"></td>
                    <td style="text-align: right;">
                        <h1 style="color: red; margin: 0;">INVOICE</h1>
                        <p>Date: {d['Tgl']}</p>
                    </td>
                </tr>
            </table>
            <hr style="border: 2px solid #1a3d8d;">
            <p><b>CUSTOMER: {d['Cust']}</b></p>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center; font-size: 12px;">
                <tr style="background: #f2f2f2;">
                    <th style="border: 1px solid black; padding: 8px;">Product Description</th>
                    <th style="border: 1px solid black;">Origin</th>
                    <th style="border: 1px solid black;">Destination</th>
                    <th style="border: 1px solid black;">Price</th>
                    <th style="border: 1px solid black;">Weight</th>
                    <th style="border: 1px solid black;">Total</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 10px; text-align: left;">{d['Produk']}</td>
                    <td style="border: 1px solid black;">{d['Asal']}</td>
                    <td style="border: 1px solid black;">{d['Tujuan']}</td>
                    <td style="border: 1px solid black;">Rp {d['Hrg']:,}</td>
                    <td style="border: 1px solid black;">{d['Brt']} Kg</td>
                    <td style="border: 1px solid black;"><b>Rp {total:,.0f}</b></td>
                </tr>
            </table>
            <div style="text-align: right; margin-top: 20px;">
                <p>Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b></p>
                <div style="position: relative; height: 80px; width: 150px; margin-left: auto;">
                    <img src="data:image/png;base64,{ttd}" style="position: absolute; width: 80px; z-index: 1; right: 30px; top: 10px;">
                    <img src="data:image/png;base64,{stempel}" style="position: absolute; width: 130px; z-index: 2; right: 0; top: 0; opacity: 0.8;">
                </div>
                <br><b>KELVINITO JAYADI</b><br>DIREKTUR
            </div>
        </div>
        """

        # KUNCI UTAMA: Gunakan unsafe_allow_html=True agar tidak muncul kode
        st.markdown(html_invoice, unsafe_allow_html=True)
