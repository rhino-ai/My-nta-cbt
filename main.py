import streamlit as st
import fitz
from PIL import Image
import io
import json
import zipfile

st.set_page_config(layout="wide", page_title="NTA Exam Portal")
st.title("🤖 My AI CBT & Auto-Cropper")

# --- NAVIGATION ---
menu = st.sidebar.radio("Go to:", ["Admin: Auto-Crop PDF", "Student: Start Test"])

if menu == "Admin: Auto-Crop PDF":
    st.header("📤 PDF Upload & Auto-Slicing")
    file = st.file_uploader("Select Question PDF", type="pdf")
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        if st.button("Process & Save Test"):
            images = []
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.open(io.BytesIO(pix.tobytes()))
                w, h = img.size
                # Page ko 4 questions mein auto-kaatna
                for i in range(4):
                    crop = img.crop((0, i*(h/4), w, (i+1)*(h/4)))
                    images.append(crop)
            st.session_state['test_paper'] = images
            st.success(f"Done! {len(images)} Questions ready for Test.")

elif menu == "Student: Start Test":
    if 'test_paper' in st.session_state:
        c1, c2 = st.columns([3, 1])
        with c1:
            q_no = st.slider("Question Palette", 1, len(st.session_state['test_paper']))
            st.image(st.session_state['test_paper'][q_no-1])
            st.radio("Options", ["A", "B", "C", "D"], key=f"q{q_no}")
            st.button("Save & Next")
        with c2:
            st.write("Timer: 03:00:00")
            st.write("Visit questions below:")
            st.button("Submit Final Test")
    else:
        st.warning("Pehle Admin panel mein PDF upload karein.")
