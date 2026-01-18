import streamlit as st
from PIL import Image

# CSS untuk mematikan klik kanan dan menyembunyikan menu
st.markdown("""
    <style>
        img { pointer-events: none; } /* Mencegah user klik kanan/drag gambar */
        #MainMenu { visibility: hidden; } /* Sembunyikan menu 3 garis */
        footer { visibility: hidden; } /* Sembunyikan footer "Made with Streamlit" */
    </style>
    """, unsafe_allow_html=True)


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

# Sembunyikan menu default, footer, dan matikan klik kanan pada gambar
hide_menu_style = """
        <style>
        /* Sembunyikan Menu Streamlit (Hamburger & Footer) */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Mencegah klik kanan pada gambar (pointer-events) */
        img {
            pointer-events: none;
            -webkit-user-select: none; /* Safari */        
            -moz-user-select: none; /* Firefox */
            -ms-user-select: none; /* IE10+/Edge */
            user-select: none; /* Standard */
        }
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


