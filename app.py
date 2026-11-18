import streamlit as st
import google.generativeai as genai
import time

# Mengatur tampilan halaman web
st.set_page_config(page_title="Mesin Novel Alia", page_icon="✍️", layout="centered")

st.title("Mesin Penulis Novel (Mode Hemat Kuota)")
st.markdown("Sekali klik untuk menulis. Sistem 1 Bab = 1 Request API. Sempurna untuk target cerpen atau bab 1.000 kata.")

# 1. KOLOM INPUT PENGGUNA
api_key = st.text_input("Masukkan Google Gemini API Key:", type="password")

gaya_default = """Bertindaklah sebagai Alia Katarina, seorang novelis profesional.
GENRE: Dark realism, romansa psikologis, dan sentuhan misteri/detektif.
NADA: Emosional, tajam, dan mengalir. Padukan realisme yang membumi dengan intrik psikologis.
DIALOG: Natural, realistis, kadang canggung, tidak dibuat-buat.
DESKRIPSI: Kuatkan detail sensorik (aroma, cuaca, gestur kecil).
PANTANGAN: Jangan menggurui pembaca. Jangan gunakan tanda baca em-dash (—). Jangan berikan penyelesaian klise. Hindari ambiguitas alur."""

konteks_utama = st.text_area("Pengaturan Gaya Bahasa:", value=gaya_default, height=220)

outline_default = """Bab 1: Pengenalan karakter utama saat berteduh dari hujan di Stasiun Tugu. Tunjukkan kegelisahannya.
Bab 2: Pertemuan tak terduga dengan teman masa lalu di Dongeng Kopi. Dialog canggung namun penuh nostalgia.
Bab 3: Konflik batin di dalam mobil saat menyusuri jalanan malam, berujung pada keputusan besar."""

outline_input = st.text_area("Masukkan Outline (Satu baris = Satu bab):", value=outline_default, height=150)

if "novel_text" not in st.session_state:
    st.session_state.novel_text = ""

# 2. MESIN PENULISAN (TOMBOL MULAI)
if st.button("🚀 Mulai Tulis (Sekali Klik)"):
    if not api_key:
        st.error("API Key wajib diisi untuk mulai menulis!")
    else:
        genai.configure(api_key=api_key)
        
        # MENGGUNAKAN MODEL YANG DIMINTA OLEH GOOGLE
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Membersihkan baris kosong dari outline
        daftar_bab = [baris.strip() for baris in outline_input.split('\n') if baris.strip()]
        novel_lengkap = ""
        
        for i, bab in enumerate(daftar_bab):
            nomor_bab = i + 1
            status_text.info(f"Mengerjakan Bab {nomor_bab} dari {len(daftar_bab)}...")
            
            try:
                # CHUNK TUNGGAL: LANGSUNG 1 BAB UTUH
                prompt = f"{konteks_utama}\n\nOutline Bab {nomor_bab}: {bab}\n\nTugas: Tuliskan bab ini secara utuh dari awal sampai akhir (target sekitar 1000 kata). Bangun adegan, konflik, dan berikan penutup yang berkesan selaras dengan outline. JANGAN dipotong di tengah jalan."
                
                res = model.generate_content(prompt)
                teks_bab = res.text
                
                # Menjahit bab
                bab_utuh = f"\n\n==================== BAB {nomor_bab} ====================\n\n{teks_bab}\n\n"
                novel_lengkap += bab_utuh
                
                status_text.success(f"Bab {nomor_bab} selesai.")
                time.sleep(5) # Jeda istirahat agar mesin tidak kepanasan (rate limit)
                
            except Exception as e:
                st.error(f"Mesin tersendat di Bab {nomor_bab}: {e}")
                break
            
            progress_bar.progress((i + 1) / len(daftar_bab))
            
        st.session_state.novel_text = novel_lengkap
        status_text.success("🎉 Seluruh bab berhasil ditulis!")

# 3. TOMBOL UNDUH
if st.session_state.novel_text:
    st.download_button(
        label="📥 Unduh Draft Lengkap (TXT)",
        data=st.session_state.novel_text,
        file_name="Tulisan_Alia_Otomatis.txt",
        mime="text/plain"
    )
