import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import pandas as pd
import plotly.express as px

# --- NTA LOOK CONFIG ---
st.set_page_config(layout="wide", page_title="NTA Exam Portal")

# CSS for Green/Red palette
st.markdown("""
<style>
    .q-palette { display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
if 'test_data' not in st.session_state: st.session_state.test_data = []
if 'responses' not in st.session_state: st.session_state.responses = {}
if 'current_q' not in st.session_state: st.session_state.current_q = 0

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Admin: Create Test", "Student: Exam Hall", "Analysis"])

if menu == "Admin: Create Test":
    st.header("📤 Step 1: Upload Question PDF")
    pdf = st.file_uploader("Upload Exam PDF", type="pdf")
    if pdf:
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        if st.button("🤖 AI: Extract Questions"):
            temp = []
            for page in doc:
                blocks = page.get_text("blocks")
                for b in blocks:
                    if "Q." in b[4] or (b[4].strip() and b[4].strip()[0].isdigit()):
                        pix = page.get_pixmap(clip=fitz.Rect(b[:4]), matrix=fitz.Matrix(2,2))
                        temp.append({"img": Image.open(io.BytesIO(pix.tobytes())), "text": b[4]})
            st.session_state.test_data = temp
            st.success(f"Successfully Extracted {len(temp)} Questions!")

elif menu == "Student: Exam Hall":
    if not st.session_state.test_data:
        st.warning("Pehle Admin section mein PDF upload karein.")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            q_idx = st.session_state.current_q
            st.subheader(f"Question {q_idx + 1}")
            st.image(st.session_state.test_data[q_idx]['img'])
            ans = st.radio("Options", ["A", "B", "C", "D"], key=f"q_{q_idx}")
            st.session_state.responses[q_idx] = ans
            if st.button("Save & Next"):
                st.session_state.current_q = min(q_idx + 1, len(st.session_state.test_data)-1)
                st.rerun()
        with col2:
            st.write("### Timer: 180:00")
            st.write("### Palette")
            for i in range(len(st.session_state.test_data)):
                if st.button(f"{i+1}", key=f"p_{i}"):
                    st.session_state.current_q = i
                    st.rerun()

elif menu == "Analysis":
    st.header("📊 Result Analytics")
    # Sample graph like your requirement
    res_df = pd.DataFrame({"Subject": ["Math", "Physics", "Chem"], "Score": [45, 30, 50]})
    fig = px.bar(res_df, x="Subject", y="Score", title="Subject-wise Analysis")
    st.plotly_chart(fig)
