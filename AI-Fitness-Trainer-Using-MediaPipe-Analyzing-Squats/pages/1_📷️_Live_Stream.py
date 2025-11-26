import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder

# --- 1. PERBAIKAN PATH (Lebih Aman untuk Cloud) ---
# Mengambil path absolut folder tempat file ini berada (folder 'pages')
current_dir = os.path.dirname(os.path.abspath(__file__))
# Naik satu level ke atas untuk dapat folder root project
root_dir = os.path.dirname(current_dir)
# Masukkan ke sys.path agar Python bisa baca file utils.py dkk
sys.path.append(root_dir)

st.title('PostureSense by RAGABISA')

# --- 2. IMPORT DENGAN ERROR HANDLING (Debugging) ---
# Ini akan menangkap error "libGL" atau "Module not found" dan menampilkannya di UI
try:
    from utils import get_mediapipe_pose
    from process_frame import ProcessFrame
    from thresholds import get_thresholds_beginner, get_thresholds_pro
except ImportError as e:
    st.error("⚠️ Terjadi kesalahan fatal saat mengimport library Computer Vision.")
    st.code(f"Error Detail: {e}")
    st.info("Kemungkinan penyebab: Library OS (libGL) belum terinstall atau struktur folder salah.")
    st.stop() # Berhenti di sini agar tidak crash parah

# --- KODE UTAMA ---

mode = st.radio('Select Mode', ['Beginner', 'Pro'], horizontal=True)

thresholds = None 

if mode == 'Beginner':
    thresholds = get_thresholds_beginner()
elif mode == 'Pro':
    thresholds = get_thresholds_pro()

# Inisialisasi Class ProcessFrame
# Pastikan library grafis sudah siap sebelum memanggil ini
try:
    live_process_frame = ProcessFrame(thresholds=thresholds, flip_frame=True)
    pose = get_mediapipe_pose()
except Exception as e:
    st.error("Gagal menginisialisasi MediaPipe/OpenCV.")
    st.write(e)
    st.stop()

if 'download' not in st.session_state:
    st.session_state['download'] = False

output_video_file = f'output_live.flv'

def video_frame_callback(frame: av.VideoFrame):
    try:
        frame = frame.to_ndarray(format="rgb24")  # Decode and get RGB frame
        
        # Proses frame menggunakan MediaPipe/OpenCV
        # Pastikan process_frame.py mengembalikan format yang benar
        frame, _ = live_process_frame.process(frame, pose)  
        
        return av.VideoFrame.from_ndarray(frame, format="rgb24")
    except Exception as e:
        # Jika error saat processing frame, kembalikan frame asli biar ga black screen
        return frame

def out_recorder_factory() -> MediaRecorder:
        return MediaRecorder(output_video_file)

# Konfigurasi WebRTC
ctx = webrtc_streamer(
                        key="Squats-pose-analysis",
                        video_frame_callback=video_frame_callback,
                        # STUN Server Google (Standard Public)
                        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  
                        media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
                        video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
                        out_recorder_factory=out_recorder_factory
                    )

download_button = st.empty()

if os.path.exists(output_video_file):
    with open(output_video_file, 'rb') as op_vid:
        download = download_button.download_button('Download Video', data = op_vid, file_name='output_live.flv')

        if download:
            st.session_state['download'] = True

if os.path.exists(output_video_file) and st.session_state['download']:
    try:
        os.remove(output_video_file)
        st.session_state['download'] = False
        download_button.empty()
    except OSError:
        pass # Abaikan jika gagal hapus sementara
