import streamlit as st
import os

st.title('PostureSense by RAGABISA')

# --- BAGIAN PERBAIKAN (DevOps Best Practice) ---

# 1. Cari tahu di mana lokasi file script (_Demo.py) ini berada di server
current_directory = os.path.dirname(os.path.abspath(__file__))

# 2. Gabungkan lokasi folder script dengan nama file video
# Hasilnya jadi path lengkap, misal: /mount/src/repo/folder/output_sample.mp4
video_path = os.path.join(current_directory, 'output_sample.mp4')

# 3. Debugging: Cek apakah file benar-benar ada sebelum di-load
if os.path.exists(video_path):
    sample_vid = st.empty()
    sample_vid.video(video_path)
else:
    # Jika file tidak ketemu, tampilkan pesan error yang informatif
    st.error(f"File video tidak ditemukan!")
    st.code(f"Mencari di lokasi: {video_path}")
    
    # Tampilkan isi folder tersebut (biar ketahuan apa saja file yang ada)
    st.write("Isi folder saat ini:")
    st.write(os.listdir(current_directory))
