import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from num2words import num2words
from datetime import datetime

# --- KONFIGURASI ---
FILE_EXCEL = 'data_logistik.xlsx'

def load_data():
    if os.path.exists(FILE_EXCEL):
        return pd.read_excel(FILE_EXCEL)
    else:
        columns = ['No_Resi', 'No_Inv', 'Customer', 'Tanggal', 'Date_Load', 
                   'Description', 'Origin', 'Destination', 'Kolli', 'Harga', 'Weight', 'Total']
        return pd.DataFrame(columns=columns)

def generate_auto_no(prefix, df):
    """Menghasilkan nomor otomatis seperti 3G/INV/240126/001"""
    date_str = datetime.now().strftime("%d%m%y")
    count = len(df) + 1
    return f"3G/{prefix}/{date_str}/{count:03d}"

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Border luar kertas
    pdf.rect(5, 5, 200, 287)

    # 1. LOGO PERUSAHAAN (Ukuran Besar w=150)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 10, w=150)
    pdf.ln(15) # Jarak spasi setelah logo

    # Label "INVOICE" Tengah
    pdf.set_fill_color(200, 200, 200)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 6, "INVOICE", 1, 1, 'C', True)

    # 2. HEADER INFO (Customer, No Inv, No Resi)
    pdf.set_font("Arial", size=8)
    pdf.cell(25, 6, "CUSTOMER  :", 0)
    pdf.cell(100, 6, str(data['Customer']), 0)
    pdf.cell(25, 6, "NO.INV     :", 0)
    pdf.cell(40, 6, str(data['No_Inv']), 0, ln=True)
    
    pdf.cell(25, 6, "TANGGAL    :", 0)
    pdf.cell(100, 6, str(data['Tanggal']), 0)
    pdf.cell(25, 6, "NO.RESI    :", 0)
    pdf.cell(40, 6, str(data['No_Resi']), 0, ln=True)
    pdf.ln(2)

    # 3. TABEL UTAMA
    pdf.set_font("Arial", 'B', 7)
    pdf.set_fill_color(52, 119, 181)
    pdf.set_text_color(255, 255, 255)
    
    pdf.cell(20, 7, "Date of Load", 1, 0, 'C', True)
    pdf.cell(50, 7, "Product Description", 1, 0, 'C', True)
    pdf.cell(20, 7, "Origin", 1, 0, 'C', True)
    pdf.cell(25, 7, "Destination", 1, 0, 'C', True)
    pdf.cell(15, 7, "KOLLI", 1, 0, 'C', True)
    pdf.cell(20, 7, "HARGA", 1, 0, 'C', True)
    pdf.cell(20, 7, "WEIGHT (Kg)", 1, 0, 'C', True)
    pdf.cell(20, 7, "TOTAL", 1, 1, 'C', True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=8)
    pdf.cell(20, 10, str(data['Date_Load']), 1, 0, 'C')
    pdf.cell(50, 10, str(data['Description']), 1, 0, 'L')
    pdf.cell(20, 10, str(data['Origin']), 1, 0, 'C')
    pdf.cell(25, 10, str(data['Destination']), 1, 0, 'C')
    pdf.cell(15, 10, str(data['Kolli']), 1, 0, 'C')
    pdf.cell(20, 10, f"Rp {data['Harga']:,.0f}".replace(",", "."), 1, 0, 'R')
    pdf.cell(20, 10, str(data['Weight']), 1, 0, 'C')
    pdf.cell(20, 10, f"Rp {data['Total']:,.0f}".replace(",", "."), 1, 1, 'R')

    # 4. TOTAL & TERBILANG
    pdf.set_fill_color(160, 160, 160)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(170, 7, "YANG HARUS DI BAYAR", 1, 0, 'C', True)
    pdf.cell(20, 7, f"Rp {data['Total']:,.0f}".replace(",", "."), 1, 1, 'R', True)

    pdf.set_fill_color(220, 220, 220)
    pdf.cell(190, 5, "Terbilang :", "LR", 1, 'L', True)
    terbilang = num2words(data['Total'], lang='id').title() + " Rupiah"
    pdf.set_font("Arial", 'BI', 9)
    pdf.cell(190, 8, f"{terbilang}", "LRB", 1, 'C', True)

    # 5. TRANSFER & TANDA TANGAN DIGITAL
    pdf.ln(5)
    current_y_position = pdf.get_y()
    
    # Bagian Kiri: Info Bank
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(100, 5, "TRANSFER TO :", 0, 1)
    pdf.set_font("Arial", size=8)
    pdf.cell(100, 4, "Bank Central Asia", 0, 1)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(100, 4, "6720422334", 0, 1)
    pdf.set_font("Arial", size=8)
    pdf.cell(100, 4, "A/N ADITYA GAMA SAPUTRI", 0, 1)
    
    # Bagian Kanan: Sincerely & Tanda Tangan
    pdf.set_y(current_y_position)
    pdf.set_font("Arial", size=9)
    pdf.cell(130, 5, "", 0)
    pdf.cell(60, 5, "Sincerely,", 0, 1, 'C')
    
    if os.path.exists("ttd.png"):
        # Meletakkan gambar ttd tepat di bawah 'Sincerely'
        pdf.image("ttd.png", 145, pdf.get_y(), w=35)
    
    pdf.ln(15) # Memberi ruang agar ttd tidak menimpa nama
    
    pdf.cell(130, 5, "", 0)
    pdf.set_font("Arial", 'BU', 9)
    pdf.cell(60, 5, "KELVINITO JAYADI", 0, 1, 'C')
    
    pdf.cell(130, 5, "", 0)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(60, 5, "DIREKTUR", 0, 1, 'C')
    
    # NB Footer
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(100, 4, "NB : Jika sudah transfer mohon konfirmasi ke", 0, 1)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(100, 4, "Finance 082179799200", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
df = load_data()
st.set_page_config(page_title="Logistik App 3G", layout="wide")
st.title("🚚 Sistem Logistik - PT. Gama Gemah Gemilang")

tab1, tab2 = st.tabs(["Cek & Cetak Invoice", "Input Data Baru"])

with tab1:
    st.subheader("Cari & Cetak Invoice")
    
    if not df.empty:
        # 1. Menyiapkan daftar resi untuk dropdown
        # Kita balik urutannya agar resi terbaru muncul paling atas
        list_resi = df['No_Resi'].astype(str).unique().tolist()[::-1]
        
        # 2. Dropdown untuk memilih resi
        # index=None artinya box akan kosong di awal sampai Anda memilih
        selected_resi = st.selectbox(
            "Pilih atau Ketik Nomor Resi:",
            options=list_resi,
            index=None,
            placeholder="Pilih nomor resi yang ingin dicetak..."
        )
        
        # 3. Logika Menampilkan Data
        if selected_resi:
            # Mencari data berdasarkan pilihan dropdown
            hasil = df[df['No_Resi'].astype(str) == selected_resi]
            
            if not hasil.empty:
                row = hasil.iloc[0]
                st.markdown("---")
                st.success(f"📌 **Detail Pengiriman: {row['No_Resi']}**")
                
                # Menampilkan ringkasan informasi
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**Customer:**\n{row['Customer']}")
                    st.write(f"**Tanggal:**\n{row['Tanggal']}")
                with c2:
                    st.write(f"**Rute:**\n{row['Origin']} ➔ {row['Destination']}")
                    st.write(f"**Berat:**\n{row['Weight']} Kg")
                with c3:
                    st.write(f"**Total Tagihan:**")
                    st.subheader(f"Rp {row['Total']:,.0f}".replace(",", "."))
                
                # Tombol Cetak PDF
                pdf_bytes = generate_pdf(row)
                st.download_button(
                    label="📥 Download Invoice PDF",
                    data=pdf_bytes,
                    file_name=f"Invoice_{selected_resi.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True # Membuat tombol lebar mengikuti layar
                )
    else:
        st.warning("Database masih kosong. Silakan input data terlebih dahulu di Tab 'Input Data Baru'.")
        
            
with tab2:
    st.subheader("Form Entry Data")
    with st.form("input_form"):
        # Auto generate nomor untuk ditampilkan sebagai info
        inv_auto = generate_auto_no("INV", df)
        resi_auto = generate_auto_no("RES", df)
        
        st.write(f"**Draft Nomor:** {inv_auto} / {resi_auto}")
        
        col1, col2 = st.columns(2)
        customer = col1.text_input("Nama Customer")
        tgl = col2.date_input("Tanggal Invoice", datetime.now())
        date_load = col1.text_input("Date of Load (Contoh: 29-Des-25)")
        desc = col2.text_input("Product Description")
        
        c3, c4, c5 = st.columns(3)
        origin = c3.text_input("Origin")
        dest = c4.text_input("Destination")
        kolli = c5.text_input("Jumlah KOLLI")
        
        c6, c7 = st.columns(2)
        harga = c6.number_input("Harga Satuan", min_value=0)
        weight = c7.number_input("Weight (Kg)", min_value=0)
        
        submitted = st.form_submit_button("Simpan Data")

    # Bagian ini di luar form agar tombol download bisa muncul setelah submit
    if submitted:
        new_data = {
            'No_Resi': resi_auto, 'No_Inv': inv_auto, 'Customer': customer,
            'Tanggal': tgl.strftime("%d/%m/%Y"), 'Date_Load': date_load,
            'Description': desc, 'Origin': origin, 'Destination': dest,
            'Kolli': kolli, 'Harga': harga, 'Weight': weight, 'Total': harga * weight
        }
        # Simpan ke Excel
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_excel(FILE_EXCEL, index=False)
        
        st.success(f"Berhasil Disimpan! No Invoice: {inv_auto}")
        
        # --- FITUR OTOMATIS: LANGSUNG DOWNLOAD ---
        st.markdown("### 🖨️ Cetak Invoice Baru")
        pdf_baru = generate_pdf(new_data)
        st.download_button(
            label="📥 Langsung Download Invoice PDF",
            data=pdf_baru,
            file_name=f"Invoice_{inv_auto.replace('/', '_')}.pdf",
            mime="application/pdf"
        )
        st.balloons()