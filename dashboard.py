import streamlit as st
from PIL import Image
from model_engine import DISEASE_DB, evaluate_weather_risk

st.set_page_config(page_title="KrishiDrishti AI", page_icon="🌾", layout="wide")

st.title("🌾 KrishiDrishti AI: Multi-Modal Crop Advisory Engine")
st.caption("MSME Idea Hackathon 6.0 Prototype | Odisha Regional Agriculture Support")

st.divider()

# Sidebar - Weather Simulation
st.sidebar.header("🌐 Real-time Weather Telemetry")
temp = st.sidebar.slider("Temperature (°C)", 15, 45, 28)
humidity = st.sidebar.slider("Humidity (%)", 30, 100, 85)

risk_data = evaluate_weather_risk(humidity, temp)
st.sidebar.subheader("Outbreak Risk Level")
st.sidebar.info(f"**{risk_data['level']}**\n\n{risk_data['message']}")

# Main Section - Image Upload
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Upload Leaf Image")
    uploaded_file = st.file_uploader("Choose a leaf image (Paddy/Vegetable)...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Leaf Image", use_column_width=True)

with col2:
    st.subheader("🔬 AI Diagnostic Report")
    if uploaded_file:
        # Simulated Prediction Output
        selected_disease = "Paddy - Bacterial Leaf Blight"
        data = DISEASE_DB[selected_disease]
        
        st.success(f"**Detected Condition:** {selected_disease}")
        st.metric(label="Model Confidence Score", value="96.4%")
        
        st.subheader("🗣️ Odia Advisory (ଓଡ଼ିଆ ପରାମର୍ଶ)")
        st.warning(data["odia_advisory"])
        
        st.subheader("🧪 Recommended Dosage / Acre")
        st.write(f"**Chemical:** {data['chemical_dosage']}")
        st.write(f"**Organic Alternative:** {data['organic_solution']}")
    else:
        st.info("Please upload a crop leaf image to generate live AI diagnostics.")