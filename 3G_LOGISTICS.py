import streamlit as st
import pandas as pd
import base64
import os

# --- 1. SETTING HALAMAN ---
st.set_page_config(page_title="3G LOGISTICS", layout="wide")

# --- 2. FUNGSI GAMBAR (Penting agar logo & stempel muncul) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. DATA (Contoh data Anda) ---
data = {
    'Resi': ['INV-001'],
    'Tanggal': ['29-Des-25'],
    'Pengirim': ['BAPAK ANDI'],
    'Produk': ['SATU SET ALAT TAMBANG'],
    'Origin': ['SBY'],
    'Destination': ['MEDAN'],
    'Harga': [8500],
    'Berat': [290]
}
df = pd.DataFrame(data)

# --- 4. TAMPILAN TAB ---
tab1, tab2 = st.tabs(["Data", "Cetak Invoice"])

with tab1:
    st.dataframe(df)

with tab2:
    # Ambil data pertama
    d = df.iloc[0]
    total = d['Harga'] * d['Berat']
    
    # Load semua gambar
    logo = get_image_base64("3G.png")
    ttd = get_image_base64("TANDA TANGAN.png")
    stempel = get_image_base64("STEMPEL DAN NAMA.png")

    # --- 5. DISINI KUNCI AGAR TIDAK BERANTAKAN ---
    # Gunakan unsafe_allow_html=True
    
    invoice_html = f"""
    <div style="background: white; color: black; padding: 30px; border: 1px solid #ccc; font-family: Arial; width: 750px; margin: auto;">
        <table style="width: 100%;">
            <tr>
                <td><img src="data:image/png;base64,{logo}" width="120"></td>
                <td style="text-align: right;">
                    <h1 style="color: red; margin: 0;">INVOICE</h1>
                    <p>Date: {d['Tanggal']}</p>
                </td>
            </tr>
        </table>
        
        <hr style="border: 1px solid #1a3d8d;">
        <p><b>CUSTOMER: {d['Pengirim']}</b></p>
        
        <table style="width: 100%; border-collapse: collapse; border: 1px solid black; text-align: center;">
            <tr style="background: #eee;">
                <th style="border: 1px solid black; padding: 5px;">Description</th>
                <th style="border: 1px solid black;">Origin</th>
                <th style="border: 1px solid black;">Dest</th>
                <th style="border: 1px solid black;">Price</th>
                <th style="border: 1px solid black;">Weight</th>
                <th style="border: 1px solid black;">Total</th>
            </tr>
            <tr>
                <td style="border: 1px solid black; padding: 10px;">{d['Produk']}</td>
                <td style="border: 1px solid black;">{d['Origin']}</td>
                <td style="border: 1px solid black;">{d['Destination']}</td>
                <td style="border: 1px solid black;">Rp {d['Harga']:,}</td>
                <td style="border: 1px solid black;">{d['Berat']} Kg</td>
                <td style="border: 1px solid black;"><b>Rp {total:,.0f}</b></td>
            </tr>
        </table>

        <div style="margin-top: 30px; text-align: right;">
            <p>Sincerely,<br><b>PT. GAMA GEMAH GEMILANG</b></p>
            <div style="position: relative; height: 100px; width: 150px; float: right;">
                <img src="data:image/png;base64,{ttd}" style="position: absolute; width: 80px; z-index: 1; right: 35px; top: 10px;">
                <img src="data:image/png;base64,{stempel}" style="position: absolute; width: 130px; z-index: 2; right: 10px; top: 0px; opacity: 0.8;">
            </div>
            <div style="clear: both; margin-top: 20px;">
                <br><b>KELVINITO JAYADI</b><br>Direktur
            </div>
        </div>
    </div>
    """

    # Perintah utama agar HTML dirender sempurna
    st.markdown(invoice_html, unsafe_allow_html=True)
