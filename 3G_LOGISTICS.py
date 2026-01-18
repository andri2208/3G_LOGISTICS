import streamlit as st
from PIL import Image

# 1. PROTEKSI UI & ANTI-DOWNLOAD
# Script ini menyembunyikan menu dan mencegah klik kanan pada gambar
st.set_page_config(
    page_title="3G Logistics",
    page_icon="FAVICON.png",
    layout="wide"
)

st.markdown("""
    <style>
    /* Mencegah klik kanan dan drag pada gambar */
    img {
        pointer-events: none;
        -webkit-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
    
    /* Menyembunyikan elemen Streamlit untuk tampilan bersih */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Pengaturan spasi untuk area tanda tangan manual */
    .signature-space {
        margin-top: 100px;
        border-bottom: 1px solid #000;
        width: 250px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER INVOICE
try:
    st.image("HEADER INVOICE.png", use_container_width=True)
except:
    st.warning("File HEADER INVOICE.png tidak ditemukan di repository.")

# 3. KONTEN APLIKASI
st.title("Sistem Manajemen Logistik")
st.write("---")

# Contoh Form Input Data (Bisa Anda sesuaikan)
col1, col2 = st.columns(2)

with col1:
    customer_name = st.text_input("Nama Pelanggan")
    no_invoice = st.text_input("Nomor Invoice")

with col2:
    tgl_kirim = st.date_input("Tanggal Pengiriman")
    keterangan = st.text_area("Keterangan Barang")

# Tabel Item (Contoh Sederhana)
st.subheader("Rincian Pengiriman")
# Anda bisa menambahkan logika tabel atau perhitungan harga di sini

# 4. AREA TANDA TANGAN (KOSONG UNTUK MANUAL)
st.write("##")
st.write("##")
col_sign1, col_sign2, col_sign3 = st.columns([1, 1, 1])

with col_sign3:
    st.write("Hormat Kami,")
    # Memberikan ruang kosong untuk stempel/tanda tangan basah nantinya
    st.markdown('<div class="signature-space"></div>', unsafe_allow_html=True)
    st.write("Administrasi 3G Logistics")

# Tombol Cetak (Hanya memicu fungsi print browser)
if st.button("Persiapkan Cetak"):
    st.info("Gunakan kombinasi tombol Ctrl+P atau Cmd+P untuk mencetak ke PDF.")
