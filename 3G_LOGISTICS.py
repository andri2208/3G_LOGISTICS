import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import streamlit.components.v1 as components
import re

# 1. KONFIGURASI HALAMAN (Update Favicon)
st.set_page_config(
    page_title="3G Logistics", 
    page_icon="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/FAVICON.png", # Link ke file favicon Bapak
    layout="wide"
)

# --- TAMBAHAN 1: SESSION STATE UNTUK KONTROL TAB ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0 # Default ke tab Invoice

# GANTI DENGAN URL BARU HASIL DEPLOY TADI
API_URL = "https://script.google.com/macros/s/AKfycbxuYkIlCrPVRtRKxj5zR6o8BRwxVFemut8hpePywTfsSwryZR2mya7GiYm_0ZY7SiDWWw/exec"

@st.cache_data(ttl=1, show_spinner=False) # Tambahkan show_spinner=False
def get_data():
    try:
        response = requests.get(f"{API_URL}?nocache={datetime.now().timestamp()}", timeout=15)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# --- CSS: HEADER AMAN & TAMPILAN BERSIH ---
st.markdown("""
    <style>
    .stApp { background-color: #FDFCF0; }
    .block-container { padding-top: 4rem !important; }
    .custom-header { text-align: left; /* PINDAH KE KIRI */ margin-bottom: 20px; }
    .custom-header img { width: 100%; max-width: 500px; height: auto; border-radius: 8px; }
    .stWidgetLabel p { font-weight: 900 !important; font-size: 14px !important; color: #1A2A3A !important; }
    .stTextInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #BCC6CC !important;
        border-radius: 8px !important;
    }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold !important; }
    /* Menyembunyikan indikator running di pojok kanan atas */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* MENGHILANGKAN TULISAN RUNNING GET_DATA */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* CSS Bapak yang sebelumnya tetap dipertahankan di bawah ini */
    .stApp { background-color: #FDFCF0; }
    .custom-header { text-align: left; margin-bottom: 20px; }
    .custom-header img { width: 100%; max-width: 400px; height: auto; border-radius: 8px; }
    </style>
    
    <div class="custom-header">
        <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png">
    </div>
    """, unsafe_allow_html=True)

# (Fungsi extract_number dan terbilang tetap sama seperti kode Bapak)
def extract_number(value):
    if pd.isna(value) or value == "": return 0
    match = re.findall(r"[-+]?\d*\.\d+|\d+", str(value).replace(',', '').replace('Kg', '').replace('kg', ''))
    if match: return float(match[0])
    return 0

def terbilang(n):
    bil = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    if n < 12: return bil[int(n)]
    elif n < 20: return terbilang(n - 10) + " Belas"
    elif n < 100: return terbilang(n // 10) + " Puluh " + terbilang(n % 10)
    elif n < 200: return " Seratus " + terbilang(n - 100)
    elif n < 1000: return terbilang(n // 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000: return " Seribu " + terbilang(n - 1000)
    elif n < 1000000: return terbilang(n // 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000: return terbilang(n // 1000000) + " Juta " + terbilang(n % 1000000)
    return ""

# --- TAMBAHAN 2: GUNAKAN SESSION STATE PADA TABS ---
# Ini agar Streamlit tahu tab mana yang harus dibuka saat rerun
tab_list = ["📄 CETAK INVOICE", "➕ TAMBAH DATA"]
tab1, tab2 = st.tabs(tab_list)

with tab1:
    data = get_data()
    if not data:
        st.info("Menunggu data dari Google Sheets...")
    else:
        # SEMUA BARIS DI BAWAH INI HARUS MASUK KE DALAM (ADA 2 KALI TAB/SPASI)
        df = pd.DataFrame(data)
        
        # Filter Status (Tambahan baru)
        st.write("---")
        c_stat1, c_stat2 = st.columns([2, 3])
        with c_stat1:
            status_filter = st.radio("Filter Status Bayar:", ["Semua", "Belum Bayar", "Lunas"], horizontal=True)
        
        if status_filter != "Semua":
            # Pastikan kolom 'status' sudah Bapak buat di Google Sheets
            if 'status' in df.columns:
                df = df[df['status'] == status_filter]
        
        # Cek lagi apakah setelah difilter datanya masih ada
        if not df.empty and 'customer' in df.columns:
            selected_cust = st.selectbox("PILIH CUSTOMER:", sorted(df['customer'].unique()))
            row = df[df['customer'] == selected_cust].iloc[-1]
            
            
            b_val = extract_number(row['weight'])
            h_val = extract_number(row['harga'])
            t_val = int(b_val * h_val) if b_val > 0 else int(h_val)
            
            tgl_raw = str(row['date']).split('T')[0]
            try:
                tgl_indo = datetime.strptime(tgl_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                tgl_indo = tgl_raw
                
            kata_terbilang = terbilang(t_val) + " Rupiah"

            # (Seluruh isi invoice_html Bapak tetap sama sampai bawah...)
            invoice_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                <style>
                    body {{ background: #f0f0f0; padding: 10px; }}
                    #inv {{ background: white; padding: 25px; width: 750px; margin: auto; border: 1px solid #ccc; color: black; font-family: Arial; }}
                    .header-img {{ width: 100%; height: auto; }}
                    .title {{ text-align: center; border-top: 2px solid black; border-bottom: 2px solid black; margin: 15px 0; padding: 5px; font-weight: bold; font-size: 20px; }}
                    .info-table {{ width: 100%; margin-bottom: 10px; font-size: 14px; font-weight: bold; }}
                    .data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; }}
                    .data-table th, .data-table td {{ border: 1px solid black; padding: 10px; }}
                    .data-table th {{ background-color: #f2f2f2; }}
                    .terbilang {{ border: 1px solid black; padding: 10px; margin-top: 10px; font-size: 12px; font-style: italic; }}
                    .footer-table {{ width: 100%; margin-top: 30px; font-size: 12px; line-height: 1.5; }}
                    .btn-dl {{ width: 750px; display: block; margin: 20px auto; background: #1A2A3A; color: white; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 16px; }}
                </style>
            </head>
            <body>
                <div id="inv">
                    <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER.png" class="header-img">
                    <div class="title">INVOICE</div>
                    <table class="info-table">
                        <tr><td>CUSTOMER: {row['customer']}</td><td style="text-align:right;">DATE: {tgl_indo}</td></tr>
                    </table>
                    <table class="data-table">
                        <thead>
                            <tr><th>Description</th><th>Origin</th><th>Dest</th><th>KOLLI</th><th>HARGA</th><th>WEIGHT</th><th>TOTAL</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>{row['description']}</td><td>{row['origin']}</td><td>{row['destination']}</td>
                                <td>{row['kolli']}</td><td>Rp {int(h_val):,}</td><td>{row['weight']}</td><td style="font-weight:bold;">Rp {t_val:,}</td>
                            </tr>
                            <tr style="font-weight:bold;"><td colspan="6" style="text-align:right;">TOTAL BAYAR</td><td>Rp {t_val:,}</td></tr>
                        </tbody>
                    </table>
                    <div class="terbilang"><b>Terbilang:</b> {kata_terbilang}</div>
                    <table class="footer-table">
                        <tr>
                            <td style="width:65%; vertical-align:top;">
                                <b>TRANSFER TO :</b><br>
                                BCA <b>6720422334</b><br>
                                <b>ADITYA GAMA SAPUTRI</b><br>
                                NB: Jika sudah transfer mohon konfirmasi ke<br>
                                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Finance: <b>082179799200</b>
                            </td>
                            <td style="text-align:center; vertical-align:top;">
                                Sincerely,<br>
                                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL.png" style="width:110px; margin: 5px 0;"><br>
                                <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                            </td>
                        </tr>
                    </table>
                </div>
                <button class="btn-dl" onclick="savePDF()">📥 DOWNLOAD PDF A5</button>
                <script>
                    function savePDF() {{
                        const e = document.getElementById('inv');
                        html2pdf().set({{ margin: 0, filename: 'Inv_{selected_cust}.pdf', image: {{ type: 'jpeg', quality: 0.98 }}, html2canvas: {{ scale: 3, useCORS: true }}, jsPDF: {{ unit: 'in', format: 'a5', orientation: 'landscape' }} }}).from(e).save();
                    }}
                </script>
            </body>
            </html>
            """
            components.html(invoice_html, height=850, scrolling=True)
        else:
            st.warning("Kolom 'customer' tidak ditemukan di Google Sheets.")

with tab2:
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 2, 2])
        v_tgl = c1.date_input("TANGGAL", datetime.now())
        v_cust = c2.text_input("NAMA CUSTOMER")
        v_desc = c3.text_input("DESKRIPSI BARANG")
        
        c4, c5, c6, c7, c8 = st.columns([1, 1, 1, 1, 1.5])
        v_orig = c4.text_input("DARI", value="SBY")
        v_dest = c5.text_input("TUJUAN")
        v_kol = c6.text_input("KOLLI")
        v_kg = c7.text_input("WEIGHT")
        v_hrg = c8.text_input("HARGA")
        
       # --- BAGIAN TOMBOL SIMPAN DI TAB 2 ---
        if st.form_submit_button("💾 SIMPAN DATA"):
            h_num = extract_number(v_hrg)
            w_num = extract_number(v_kg)
            weight_final = str(v_kg)
            if v_kg and "kg" not in v_kg.lower(): weight_final = f"{v_kg} Kg"
            
            total_db = int(w_num * h_num) if w_num > 0 else int(h_num)
            
            payload = {
                "date": str(v_tgl), 
                "customer": v_cust.upper(), 
                "description": v_desc.upper(),
                "origin": v_orig.upper(), 
                "destination": v_dest.upper(), 
                "kolli": v_kol,
                "harga": h_num, 
                "weight": weight_final, 
                "total": total_db,
                "status": "Belum Bayar"  # <--- TAMBAHKAN INI DI PAYLOAD PYTHON
            }
            
            try:
                # Menampilkan spinner agar user tahu proses sedang berjalan
                with st.spinner('Sedang mengirim data...'):
                    r = requests.post(API_URL, data=json.dumps(payload))
                    
                if r.status_code == 200:
                    # NOTIFIKASI BERHASIL
                    st.success(f"✅ DATA {v_cust.upper()} BERHASIL DISIMPAN, BUKA TAB CETAK INVOICE!")
                    
                    # Beri jeda 1 detik agar user sempat membaca notifikasi
                    import time
                    time.sleep(1.5) 
                    
                    # Refresh dan Pindah Tab
                    st.cache_data.clear()
                    st.session_state.active_tab = 0 
                    st.rerun()
                else:
                    st.error(f"❌ GAGAL MENYIMPAN! Status: {r.status_code}")
            except Exception as e:
                st.error(f"⚠️ Terjadi Kesalahan: {str(e)}")



















