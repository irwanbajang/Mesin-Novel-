import streamlit as st
import google.generativeai as genai
import time

# Mengatur tampilan halaman web di HP
st.set_page_config(page_title="Mesin Novel Alia", page_icon="✍️", layout="centered")

st.title("Mesin Penulis Novel 3.000 Kata")
st.markdown("Sekali klik untuk menulis 15-20 bab sekaligus. Sistem otomatis menyambung 3 bagian (Awal, Tengah, Akhir) per bab agar mencapai target kata.")

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

# Tempat menyimpan hasil sementara agar tidak hilang saat layar HP direfresh
if "novel_text" not in st.session_state:
    st.session_state.novel_text = ""

# 2. MESIN PENULISAN (TOMBOL MULAI)
if st.button("🚀 Mulai Tulis Novel (Sekali Klik)"):
    if not api_key:
        st.error("API Key wajib diisi untuk mulai menulis!")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Membersihkan baris kosong dari outline
        daftar_bab = [baris.strip() for baris in outline_input.split('\n') if baris.strip()]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        novel_lengkap = ""
        
        for i, bab in enumerate(daftar_bab):
            nomor_bab = i + 1
            status_text.info(f"Mengerjakan Bab {nomor_bab} dari {len(daftar_bab)}...")
            
            try:
                # CHUNK 1: BAGIAN AWAL (~1000 kata)
                status_text.warning(f"Bab {nomor_bab}: Menulis Bagian Awal...")
                prompt_1 = f"{konteks_utama}\n\nOutline Bab {nomor_bab}: {bab}\n\nTugas: Tuliskan BAGIAN AWAL dari bab ini (target 1000 kata). Bangun adegan, suasana, dan percakapan awal. Berhenti secara natural di tengah adegan, JANGAN selesaikan bab ini."
                res_1 = model.generate_content(prompt_1)
                teks_awal = res_1.text
                time.sleep(5)
                
                # CHUNK 2: BAGIAN TENGAH (~1000 kata)
                status_text.warning(f"Bab {nomor_bab}: Menulis Bagian Tengah...")
                prompt_2 = f"{konteks_utama}\n\nOutline Bab {nomor_bab}: {bab}\n\nBerikut adalah BAGIAN AWAL yang baru saja kamu tulis:\n{teks_awal}\n\nTugas: Lanjutkan cerita langsung dari titik terakhir di atas untuk BAGIAN TENGAH (target 1000 kata). Eksplorasi konflik, batin karakter, dan eskalasi. JANGAN tamatkan bab ini."
                res_2 = model.generate_content(prompt_2)
                teks_tengah = res_2.text
                time.sleep(5)
                
                # CHUNK 3: BAGIAN AKHIR (~1000 kata)
                status_text.warning(f"Bab {nomor_bab}: Menulis Bagian Akhir...")
                prompt_3 = f"{konteks_utama}\n\nOutline Bab {nomor_bab}: {bab}\n\nBerikut adalah cerita sejauh ini:\n{teks_awal}\n{teks_tengah}\n\nTugas: Lanjutkan dan SELESAIKAN bab ini (target 1000 kata). Berikan penutup yang berkesan dan selaras dengan outline."
                res_3 = model.generate_content(prompt_3)
                teks_akhir = res_3.text
                
                # Menjahit ketiga bagian menjadi satu bab utuh
                bab_utuh = f"\n\n==================== BAB {nomor_bab} ====================\n\n{teks_awal}\n\n{teks_tengah}\n\n{teks_akhir}\n\n"
                novel_lengkap += bab_utuh
                
                status_text.success(f"Bab {nomor_bab} selesai (~3.000 kata).")
                time.sleep(10) 
                
            except Exception as e:
                st.error(f"Mesin tersendat di Bab {nomor_bab}: {e}")
                break
            
            progress_bar.progress((i + 1) / len(daftar_bab))
            
        st.session_state.novel_text = novel_lengkap
        status_text.success("🎉 Seluruh bab berhasil ditulis!")

# 3. TOMBOL UNDUH (DOWNLOAD)
if st.session_state.novel_text:
    st.download_button(
        label="📥 Unduh Draft Novel Lengkap (TXT)",
        data=st.session_state.novel_text,
        file_name="Novel_Alia_Otomatis.txt",
        mime="text/plain"
              )
  
