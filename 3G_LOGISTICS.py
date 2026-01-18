import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Menggunakan FAVICON.png yang ada di folder Anda
st.set_page_config(page_title="3G LOGISTICS", page_icon="FAVICON.png", layout="wide")

# Menampilkan HEADER INVOICE.png
st.image("HEADER INVOICE.png", use_container_width=True)

st.title("Sistem Logistik PT. GAMA GEMAH GEMILANG")

# Koneksi ke Google Sheets menggunakan Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Membaca data (Misal sheet bernama 'Data_Logistik')
try:
    df = conn.read(worksheet="Sheet1")
    st.success("Koneksi ke Database Berhasil!")
    
    # Menampilkan data dalam tabel
    st.subheader("Daftar Pengiriman")
    st.dataframe(df)
    
except Exception as e:
    st.error(f"Gagal memuat data. Pastikan Secrets sudah disetting. Error: {e}")

# Bagian Stempel (Contoh jika ingin ditampilkan di bawah)
if st.button("Lihat Stempel"):
    st.image("STEMPEL TANDA TANGAN.png", width=200)
