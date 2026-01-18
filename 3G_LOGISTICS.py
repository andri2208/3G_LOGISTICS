import streamlit as st
import pandas as pd
import requests
import json
import streamlit.components.v1 as components

# 1. SETTING HALAMAN
st.set_page_config(page_title="3G System", layout="wide")

# 2. CSS BIAR RAPI
st.markdown("""
    <style>
    header {visibility: hidden;}
    .stTabs { margin-top: -20px; }
    #print-area { background: white; padding: 20px; }
    @media only screen and (max-width: 600px) {
        #print-area { zoom: 0.5; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🔐 Login 3G Logistics")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if u == "admin3g" and p == "gama2024":
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Salah!")
else:
    API = "https://script.google.com/macros/s/AKfycbxRDbA4sWrueC3Vb2Sol8UzUYNTzgghWUksBxvufGEFgr7iM387ZNgj8JPZw_QQH5sO/exec"

    def terbilang(n):
        bil = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
        if n < 12: return bil[int(n)]
        elif n < 20: return terbilang(n - 10) + " belas"
        elif n < 100: return terbilang(n // 10) + " puluh " + terbilang(n % 10)
        elif n < 200: return " seratus " + terbilang(n - 100)
        elif n < 1000: return terbilang(n // 100) + " ratus " + terbilang(n % 100)
        elif n < 2000: return " seribu " + terbilang(n - 1000)
        elif n < 1000000: return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
        elif n < 1000000000: return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
        return ""

    # TOMBOL LOGOUT
    if st.sidebar.button("Keluar / Logout"):
        st.session_state['auth'] = False
        st.rerun()

    tab1, tab2 = st.tabs(["📄 Cetak Invoice", "➕ Tambah Data"])

    with tab1:
        try:
            res = requests.get(API).json()
            df = pd.DataFrame(res)
            nama = st.selectbox("Pilih Customer", df['customer'].unique())
            r = df[df['customer'] == nama].iloc[-1]
            tgl = str(r['date']).split('T')[0]
            total = int(r['total'])
            kata = terbilang(total).title() + " Rupiah"

            # INVOICE HTML (GARIS DIJAMIN NYAMBUNG)
            html = f"""
            <div id="print-area" style="width:750px; margin:auto; border:2px solid black; padding:30px; font-family:Arial;">
                <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/HEADER%20INVOICE.png" style="width:100%;">
                <div style="text-align:center; border-top:2px solid black; border-bottom:2px solid black; margin:10px 0; padding:5px; font-weight:bold; font-size:20px;">INVOICE</div>
                <table style="width:100%; font-weight:bold; margin-bottom:10px;">
                    <tr><td>CUSTOMER: {nama}</td><td style="text-align:right;">DATE: {tgl}</td></tr>
                </table>
                <table style="width:100%; border-collapse:collapse; border:1px solid black;">
                    <tr style="background:#316395; color:white; text-align:center;">
                        <th style="border:1px solid black; padding:8px;">Description</th>
                        <th style="border:1px solid black;">Origin</th>
                        <th style="border:1px solid black;">Dest</th>
                        <th style="border:1px solid black;">KOLLI</th>
                        <th style="border:1px solid black;">Price</th>
                        <th style="border:1px solid black;">Weight</th>
                    </tr>
                    <tr style="text-align:center; height:60px;">
                        <td style="border:1px solid black;">{r['description']}</td>
                        <td style="border:1px solid black;">{r['origin']}</td>
                        <td style="border:1px solid black;">{r['destination']}</td>
                        <td style="border:1px solid black;">{r['kolli']}</td>
                        <td style="border:1px solid black;">Rp {int(r['harga']):,}</td>
                        <td style="border:1px solid black;">{r['weight']} Kg</td>
                    </tr>
                    <tr style="font-weight:bold; background:#eee;">
                        <td colspan="5" style="border:1px solid black; text-align:center; padding:10px;">TOTAL BAYAR</td>
                        <td style="border:1px solid black; text-align:center;">Rp {total:,}</td>
                    </tr>
                    <tr>
                        <td colspan="6" style="border:1px solid black; padding:10px;"><b>Terbilang:</b> <i>{kata}</i></td>
                    </tr>
                </table>
                <br>
                <table style="width:100%;">
                    <tr>
                        <td style="width:60%; font-size:12px;">
                            <b>TRANSFER TO:</b><br>
                            Bank Central Asia 6720422334<br>
                            A/N ADITYA GAMA SAPUTRI<br><br>
                            NB: Jika sudah transfer mohon konfirmasi ke<br>
                            Finance 082179799200
                        </td>
                        <td style="text-align:center; font-size:12px;">
                            Sincerely,<br>
                            <img src="https://raw.githubusercontent.com/andri2208/3G_LOGISTICS/master/STEMPEL%20TANDA%20TANGAN.png" style="width:120px;"><br>
                            <b><u>KELVINITO JAYADI</u></b><br>DIREKTUR
                        </td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            
            # TOMBOL DOWNLOAD
            st.write("---")
            components.html(f"""
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
                <button onclick="save()" style="width:100%; padding:15px; background:#4CAF50; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">📥 SIMPAN PDF</button>
                <script>
                function save() {{
                    const e = window.parent.document.getElementById('print-area');
                    html2pdf().from(e).set({{ margin: 0.5, filename: 'Inv_{nama}.pdf', html2canvas: {{ scale: 2 }}, jsPDF: {{ format: 'a4', orientation: 'portrait' }} }}).save();
                }}
                </script>
            """, height=80)
        except: st.error("Gagal ambil data. Cek koneksi.")

    with tab2:
        st.subheader("Input Data Baru")
        with st.form("f1", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_tgl = c1.date_input("Tanggal")
            f_cus = c1.text_input("Customer")
            f_brg = c1.text_input("Barang")
            f_ori = c2.text_input("Origin", "SBY")
            f_des = c2.text_input("Dest")
            f_kol = c2.number_input("Kolli", 0)
            f_kg = c2.number_input("Kg", 1)
            f_hrg = c2.number_input("Harga", 0)
            if st.form_submit_button("Simpan"):
                d = {"date":str(f_tgl),"customer":f_cus.upper(),"description":f_brg.upper(),"origin":f_ori.upper(),"destination":f_des.upper(),"kolli":f_kol,"harga":f_hrg,"weight":f_kg,"total":f_hrg*f_kg}
                requests.post(API, data=json.dumps(d))
                st.success("Tersimpan!")
                st.cache_data.clear()
