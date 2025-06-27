import streamlit as st
import streamlit.components.v1 as components
import os
import datetime
import cv2
from utils.detection import detect_fault_from_image
from utils.report_gen import generate_llm_report, save_report_to_word
from utils.scraping import search_companies_web  # يستخدم Serper
from utils.drone_stream import DroneStream
from utils.download_model import ensure_model_file

# إعداد المجلدات
os.makedirs("images", exist_ok=True)
os.makedirs("reports", exist_ok=True)

st.set_page_config(page_title="Insulator Fault Detection", layout="centered")
st.title("📡 Insulator Fault Detection & Reporting AI")
st.markdown("---")

# YOLOv8 Model
ensure_model_file("model/best.pt", "https://drive.google.com/uc?export=download&id=1bZUWpRg4hhZ38EBjakNgrA0VXJVRG2W8")

# GPT4All Model
ensure_model_file("model/mistral-7b-instruct-v0.1.Q4_0", "https://drive.google.com/uc?export=download&id=1WhroioKYW1Qs0_KZzXTuhi9DGMOgC5Kc")
# === الشريط الجانبي (Sidebar) ===
with st.sidebar:
    st.header("⚙️ Settings")
    country_list = [  # اختصرنا القائمة للتنظيم
         "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
    "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia",
    "Bosnia", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
    "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
    "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Estonia", "Ethiopia",
    "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada",
    "Guatemala", "Guinea", "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran",
    "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", "Mauritius", "Mexico", "Moldova",
    "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nepal", "Netherlands", "New Zealand",
    "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine",
    "Panama", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda",
    "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Somalia", "South Africa",
    "South Korea", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan",
    "Tanzania", "Thailand", "Togo", "Trinidad", "Tunisia", "Turkey", "Turkmenistan", "Uganda", "Ukraine", "United Arab Emirates",
    "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ]
    selected_country = st.selectbox("🌍 Select your country:", country_list)

    availability = st.radio("📦 Do you already have the required insulator?", ("Yes", "No"))

    source_preference = None
    if availability == "No":
        source_preference = st.radio("🌐 Source from:", ("Local suppliers", "International suppliers"))

# === طريقة الإدخال ===
st.markdown("## Input Method")
option = st.radio(
    "Choose input method:",
    ("📁 Upload Image", "🎥 Upload Video", "🚁 Connect to Drone Stream (Live)"),
    horizontal=True,
)

file_path = None
image_frame = None
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# === التعامل مع الصورة أو الفيديو ===
if option == "📁 Upload Image":
    uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        file_path = os.path.join("images", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(file_path, caption="Uploaded Image", use_column_width=True)
        image_frame = cv2.imread(file_path)

elif option == "🎥 Upload Video":
    uploaded_video = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])
    if uploaded_video:
        file_path = os.path.join("images", uploaded_video.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_video.getbuffer())
        st.video(file_path)
        cap = cv2.VideoCapture(file_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_to_sample = min(frame_count, 5)
        detections = []
        for i in range(frames_to_sample):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * frame_count // frames_to_sample)
            success, frame = cap.read()
            if success:
                temp_path = os.path.join("images", f"frame_{i}_{timestamp}.jpg")
                cv2.imwrite(temp_path, frame)
                dets = detect_fault_from_image(temp_path)
                if dets:
                    detections.extend(dets)
        cap.release()
        if detections:
            image_frame = frame

elif option == "🚁 Connect to Drone Stream (Live)":
    stream_url = st.text_input("Enter RTSP stream URL (e.g., from DJI/ESP32)", placeholder="rtsp://...")
    if st.button("Start Drone Stream"):
        if stream_url:
            drone = DroneStream(stream_url)
            stframe = st.empty()
            frame = drone.get_frame()
            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(frame_rgb, caption="Live Frame from Drone", channels="RGB")
                image_frame = frame
                file_path = os.path.join("images", f"drone_frame_{timestamp}.jpg")
                cv2.imwrite(file_path, frame)
            else:
                st.warning("❌ Could not read frame from drone.")
            drone.release()

# === بدء التحليل والتقرير ===
if image_frame is not None:
    if 'detections' not in locals() or not detections:
        detections = detect_fault_from_image(file_path)

    if detections:
        label = detections[0]["label"]
        confidence = detections[0]["confidence"]

        st.success(f"⚠️ Detected Fault: **{label}** ({confidence:.2f})")
        st.markdown("---")

        # === بحث الموردين (حسب الاختيارات)
        companies = []
        if availability == "No":
            is_local = (source_preference == "Local suppliers")
            companies = search_companies_web(
                query="insulator electricity",
                country=selected_country,
                local=is_local
            ) or []

        # === توليد نص الموردين للتقرير
        if availability == "Yes":
            suppliers_info_text = "User already has the required insulator. No suppliers needed."
        else:
            suppliers_info_text = "\n".join([
                f"{c['name']}: {c.get('description', 'No description')}" for c in companies
            ])

        report_text = generate_llm_report(label, confidence, timestamp, suppliers_info_text)

        with st.expander("📝 View Generated Report", expanded=True):
            st.text_area("LLM Report", report_text, height=300)

        report_path = os.path.join("reports", f"Insulator_Fault_Report_{timestamp}.docx")
        save_report_to_word(
            report_text,
            filename=os.path.basename(report_path),
            output_dir="reports",
            image_path=file_path,
            suppliers=companies,
            detections=detections
        )

        with open(report_path, "rb") as f:
            st.download_button("⬇️ Download Report (.docx)", f, file_name=os.path.basename(report_path))

    else:
        st.info("✅ No faults detected in the input.")
else:
    st.info("Please upload or provide input to start detection.")
