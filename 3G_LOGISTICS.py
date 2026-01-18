import streamlit as st
import os
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="3G LOGISTICS - LOGIN",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. FUNGSI ENCODE GAMBAR ---
def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 3. CSS LUXURY EMERALD THEME & RESPONSIVE ---
logo_b64 = get_base64_img("FAVICON.png")

st.markdown(f"""
    <style>
    /* Background Utama: Dark Emerald ke Deep Charcoal */
    .stApp {{
        background: linear-gradient(135deg, #0A4A4A 0%, #1A1A1A 100%);
        background-attachment: fixed;
    }}

    /* Container Utama untuk Responsivitas */
    .main-login-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 90vh;
        padding: 20px;
    }}

    /* Card Login Elegan - Lebih Transparan */
    .login-card {{
        background: rgba(255, 255, 255, 0.03); /* Lebih transparan */
        backdrop-filter: blur(15px); /* Blur lebih lembut */
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08); /* Border lebih tipis */
        border-radius: 25px; /* Sudut lebih lembut */
        padding: 40px 30px;
        width: 100%;
        max-width: 400px; /* Card sedikit lebih kecil */
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        text-align: center;
    }}

    /* Logo Pro */
    .logo-img {{
        width: 100%;
        max-width: 250px; /* Logo sedikit lebih kecil */
        height: auto;
        margin-bottom: 25px;
    }}

    /* Teks Deskripsi */
    .brand-text {{
        color: white;
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }}

    .sub-text {{
        color: rgba(255,255,255,0.5); /* Lebih lembut */
        font-size: 0.85rem;
        margin-bottom: 35px;
    }}

    /* Styling Input */
    .stTextInput {{
        width: 100% !important;
        max-width: 300px !important; /* Kotak input tetap kecil */
        margin: 0 auto !important;
    }}
    .stTextInput > div > div > input {{
        background-color: rgba(255,255,255,0.9) !important;
        color: #1a1a1a !important;
        border-radius: 10px !important;
        height: 45px !important; /* Sedikit lebih tinggi */
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        border: none !important;
    }}

    /* Styling Button - Aksen Merah Kontras */
    .stButton > button {{
        background: linear-gradient(90deg, #FF0000 0%, #CC0000 100%) !important; /* Merah cerah */
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100% !important;
        max-width: 300px !important; /* Ikut lebar input */
        height: 45px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s all ease;
        margin-top: 15px;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 0, 0, 0.4);
        background: #FF3333 !important;
    }}

    /* Sembunyikan Elemen Streamlit */
    header, footer, #MainMenu {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* Responsivitas Layar HP */
    @media (max-width: 480px) {{
        .login-card {{
            padding: 30px 20px;
        }}
        .logo-img {{
            max-width: 180px;
        }}
        .brand-text {{
            font-size: 1.2rem;
        }}
        .sub-text {{
            font-size: 0.8rem;
        }}
        .stTextInput {{
            max-width: 250px !important;
        }}
        .stButton > button {{
            max-width: 250px !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

   
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    
    st.markdown('<div class="brand-text">PT. GAMA GEMAH GEMILANG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-text">Cargo & Logistics Management System</div>', unsafe_allow_html=True)
    
    with st.container():
        pwd = st.text_input("PASSWORD", type="password", placeholder="MASUKKAN AKSES KODE", label_visibility="collapsed")
        
        if st.button("MASUK SISTEM"):
            if pwd == "2026": # Sesuaikan dengan password Anda
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Kode Akses Salah")
                
    st.markdown('</div>', unsafe_allow_html=True) # Tutup login-card
    st.markdown('</div>', unsafe_allow_html=True) # Tutup main-login-container
    st.stop()

# --- 5. HALAMAN DASHBOARD (SETELAH LOGIN) ---
st.markdown("<style>.stApp { overflow: auto !important; }</style>", unsafe_allow_html=True)

# Pesan selamat datang yang elegan (opsional, bisa diganti)
st.markdown("""
    <div style="
        background: rgba(255,255,255,0.08); /* Glassmorphism effect */
        backdrop-filter: blur(10px);
        border-left: 4px solid #33FF33; /* Aksen hijau untuk sukses */
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 30px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    ">
        <h4 style="color: #33FF33; margin: 0;">Login Berhasil!</h4>
        <p style="color: rgba(255,255,255,0.7); margin: 5px 0 0 0;">Selamat datang di Dashboard 3G Logistics, Administrator.</p>
    </div>
""", unsafe_allow_html=True)

# Tombol Logout di dashboard
st.sidebar.markdown(f"""
    <div style="margin-top: 50px; text-align: center;">
        <button style="
            background: #FF0000;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.3s;
        " onclick="window.location.reload();">
            🚪 LOGOUT
        </button>
    </div>
""", unsafe_allow_html=True)
# Anda bisa menggunakan st.sidebar.button("Logout") jika ingin fungsionalitas Streamlit murni.

st.title("🚀 Dashboard Utama")
st.write("Di sini Anda bisa menambahkan tab untuk Create Invoice dan Database.")

# --- Bagian Dashboard (Contoh) ---
tab1, tab2 = st.tabs(["📝 CREATE INVOICE", "📂 DATABASE"])

with tab1:
    st.header("Form Input Invoice")
    st.write("Isi detail pengiriman di sini.")
    # Contoh form sederhana
    with st.form("invoice_form"):
        customer_name = st.text_input("Nama Customer")
        product_desc = st.text_input("Deskripsi Produk")
        col1, col2 = st.columns(2)
        origin = col1.text_input("Asal")
        destination = col2.text_input("Tujuan")
        col3, col4 = st.columns(2)
        price = col3.number_input("Harga per Kg", min_value=0)
        weight = col4.number_input("Berat (Kg)", min_value=0.0)
        
        if st.form_submit_button("Generate Invoice"):
            if customer_name and product_desc and origin and destination and price > 0 and weight > 0:
                total = price * weight
                st.success(f"Invoice untuk {customer_name} berhasil dibuat! Total: Rp {total:,.0f}")
                # Di sini Anda bisa menambahkan logika penyimpanan ke API atau generate PDF
            else:
                st.error("Harap isi semua kolom dengan benar.")

with tab2:
    st.header("Riwayat Transaksi")
    st.write("Tampilkan data transaksi dari database.")
    # Contoh data dummy
    data = {
        'ID Transaksi': ['TRX001', 'TRX002', 'TRX003'],
        'Customer': ['Bapak Andi', 'Ibu Budi', 'PT. Jaya Selalu'],
        'Produk': ['Mesin Industri', 'Sparepart Mobil', 'Bahan Bangunan'],
        'Total (Rp)': [15000000, 2500000, 30000000],
        'Tanggal': ['2023-01-15', '2023-01-18', '2023-01-20']
    }
    df = pd.DataFrame(data)
    st.dataframe(df)

