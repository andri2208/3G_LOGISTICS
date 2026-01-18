import streamlit as st
from PIL import Image

# 1. Konfigurasi Halaman & Favicon
# Pastikan nama file sama persis: 'FAVICON.png'
im = Image.open("FAVICON.png")
st.set_page_config(
    page_title="3G Logistics",
    page_icon=im,
    layout="wide"
)

# 2. Menampilkan Header Invoice
# Gunakan use_column_width agar responsif
st.image("HEADER INVOICE.png", use_column_width=True) 

st.title("Aplikasi Invoice & Logistik")

# --- Logika Aplikasi Anda di sini ---

# 3. Menampilkan Stempel di bagian tanda tangan (misalnya di akhir invoice)
st.write("Hormat Kami,")
st.image("STEMPEL TANDA TANGAN.png", width=200) # Atur width sesuai kebutuhan
