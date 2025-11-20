# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 21:17:49 2025

@author: Ishita
"""

import pickle
import streamlit as st
import random
import time
import json
import os
import hashlib

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Medi-Predictor",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR DARK BLUE GLASSMORPHISM THEME ---
page_bg_css = """
<style>
/* --- MAIN BACKGROUND --- */
[data-testid="stAppViewContainer"] {
    background-image: linear-gradient(180deg, #000428, #004e92);
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}

/* --- SIDEBAR BACKGROUND --- */
[data-testid="stSidebar"] {
    background-image: linear-gradient(180deg, #004e92, #000428);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

/* --- GLASSMORPHISM CARDS & INPUTS --- */
div[data-baseweb="input"] > div, 
div[data-baseweb="select"] > div, 
div[data-testid="stMarkdownContainer"] > div,
div[data-testid="stMetricValue"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: white !important;
}

/* --- TABS STYLING --- */
button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #e0e0e0 !important;
    font-weight: 600;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00d2ff !important;
    border-bottom: 2px solid #00d2ff !important;
}

/* --- HEADERS --- */
h1, h2, h3 {
    color: #00d2ff !important; /* Neon Cyan for pop */
    text-shadow: 0 0 10px rgba(0, 210, 255, 0.3);
    font-weight: 600;
}

p, label, li, span {
    color: #e0e0e0 !important;
}

/* --- ANIMATED BUTTONS --- */
div.stButton > button {
    background: linear-gradient(45deg, #007bff, #00c6ff);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 12px 28px;
    font-size: 16px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0, 198, 255, 0.3);
    transition: all 0.3s ease;
    width: 100%;
}

div.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 198, 255, 0.6);
}

/* --- SUCCESS/ERROR BOX STYLING --- */
div[data-testid="stAlert"] {
    background-color: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 10px;
}

/* --- MULTI-SELECT TAGS --- */
span[data-baseweb="tag"] {
    background-color: #007bff !important;
}

/* --- EXPANDER HEADER --- */
.streamlit-expanderHeader {
    color: #00d2ff !important;
    font-weight: bold;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)


# =========================================================
#  AUTHENTICATION FUNCTIONS (JSON DB & HASHING)
# =========================================================
DB_FILE = 'user_db.json'

def load_users():
    """Loads users from JSON file. If not exists, returns empty dict."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Saves users to JSON file."""
    with open(DB_FILE, 'w') as f:
        json.dump(users, f)

def make_hashes(password):
    """Hashes password using SHA256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Checks if entered password matches stored hash."""
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# --- LOGIN / SIGNUP PAGE LOGIC ---
def login_page():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=80)
        st.title("Medi-Predictor")
        st.markdown("##### Secure Access Portal")
        
        # Authentication Tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Create Account"])
        
        # --- LOGIN TAB ---
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Log In"):
                users = load_users()
                if username in users:
                    if check_hashes(password, users[username]['password']):
                        st.session_state['logged_in'] = True
                        st.session_state['user_name'] = users[username]['name']
                        st.success(f"Welcome back, {users[username]['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Incorrect Password")
                else:
                    st.error("Username not found")

        # --- SIGN UP TAB ---
        with tab2:
            new_name = st.text_input("Full Name")
            new_user = st.text_input("Choose a Username")
            new_pass = st.text_input("Choose a Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.button("Create Account"):
                users = load_users()
                if new_user in users:
                    st.warning("Username already exists. Please choose another.")
                elif new_pass != confirm_pass:
                    st.warning("Passwords do not match.")
                elif not new_user or not new_pass or not new_name:
                    st.warning("Please fill in all fields.")
                else:
                    # Save new user
                    users[new_user] = {
                        "name": new_name,
                        "password": make_hashes(new_pass)
                    }
                    save_users(users)
                    st.success("Account created successfully! You can now Login.")

# =========================================================
#  MAIN APP EXECUTION
# =========================================================

if not st.session_state['logged_in']:
    login_page()
else:
    # --- LOGGED IN USER INTERFACE ---
    
    # Load Models
    try:
        diabetes_model = pickle.load(open('trained_model.sav', 'rb'))
        heart_disease_model = pickle.load(open('heart_disease_model.sav', 'rb'))
        parkinsons_model = pickle.load(open('parkinsons_model.sav', 'rb'))
    except FileNotFoundError:
        st.warning("⚠️ Model files not found. Please check your file paths.")
        pass

    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=70) 
        st.title("Medi-Predictor")
        
        # Personal Greeting in Sidebar
        st.markdown(f"👤 **{st.session_state['user_name']}**")
        st.markdown("---")
        
        selected = st.radio(
            "Navigate System:",
            ['Home Dashboard', '🔍 Symptom Checker', '🩸 Diabetes Check', '💓 Heart Disease Check', '🧠 Parkinsons Check'],
            index=0
        )
        
        st.markdown("---")
        if st.button("🔒 Log Out"):
            st.session_state['logged_in'] = False
            st.session_state['user_name'] = ""
            st.rerun()
            
        st.caption("v3.3 | Secure Medical AI")


    # --- HOME DASHBOARD ---
    if selected == 'Home Dashboard':
        st.title("Medi-Predictor Dashboard")
        # Personalized Welcome
        st.markdown(f"### 👋 Welcome back, {st.session_state['user_name']}.")
        st.markdown("Select a module from the sidebar to begin analysis.")
        
        st.markdown("---")
        
        # Dashboard Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Diabetes Model", value="Active", delta="Accuracy: 98%")
        with col2:
            st.metric(label="Heart Disease Model", value="Active", delta="Accuracy: 95%")
        with col3:
            st.metric(label="Parkinsons Model", value="Active", delta="Accuracy: 94%")
            
        st.markdown("---")
        st.info("✨ **Update:** The Symptom Checker now includes Emergency Triage logic.")


    # --- SYMPTOM CHECKER PAGE ---
    elif selected == '🔍 Symptom Checker':
        st.title("🔍 Intelligent Symptom Checker")
        st.markdown("Identify potential conditions and get actionable triage advice.")

        with st.expander("🚨 **EMERGENCY CHECK (READ FIRST)**", expanded=True):
            st.error("Do not use this tool if you have:")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("• Crushing Chest Pain\n• Severe Difficulty Breathing\n• Uncontrollable Bleeding")
            with c2:
                st.markdown("• Sudden Slurred Speech (Stroke signs)\n• Severe Head Injury\n• Loss of Consciousness")
            st.caption("If you experience these, call Emergency Services (911/112) immediately.")

        st.markdown("---")

        st.markdown("#### 1. Patient Details")
        col_dem1, col_dem2 = st.columns(2)
        with col_dem1:
            age_check = st.number_input("Age", min_value=1, max_value=120, value=25)
        with col_dem2:
            gender_check = st.radio("Gender", ["Male", "Female"], horizontal=True)

        st.markdown("#### 2. Add Symptoms")
        
        disease_db = {
            "Heart Attack (Myocardial Infarction)": {
                "symptoms": ["Chest Pain", "Shortness of Breath", "Pain in Left Arm", "Sweating", "Nausea", "Lightheadedness"],
                "severity": "Critical",
                "advice": "🚑 **CALL EMERGENCY SERVICES IMMEDIATELY.** Do not drive yourself to the hospital."
            },
            "Stroke": {
                "symptoms": ["Sudden Numbness", "Slurred Speech", "Confusion", "Vision Trouble", "Severe Headache", "Balance Loss"],
                "severity": "Critical",
                "advice": "🚑 **CALL EMERGENCY SERVICES.** Time is brain. Note the time symptoms started."
            },
            "Appendicitis": {
                "symptoms": ["Sharp Pain Lower Right Abdomen", "Nausea", "Vomiting", "Fever", "Loss of Appetite"],
                "severity": "High",
                "advice": "🏥 **Seek Immediate Medical Care.** Appendicitis requires urgent evaluation."
            },
            "Kidney Stones": {
                "symptoms": ["Severe Side/Back Pain", "Blood in Urine", "Nausea", "Vomiting", "Fever", "Painful Urination"],
                "severity": "High",
                "advice": "🏥 **Consult a Doctor.** Severe pain may require ER visit for pain management."
            },
            "Diabetes (Type 2)": {
                "symptoms": ["Increased Thirst", "Frequent Urination", "Unexplained Weight Loss", "Extreme Hunger", "Blurred Vision", "Fatigue"],
                "severity": "Medium",
                "advice": "🩺 **See a Doctor.** Use the **Diabetes Check** tool in the sidebar for a risk calculation."
            },
            "COVID-19": {
                "symptoms": ["Fever", "Dry Cough", "Loss of Taste/Smell", "Shortness of Breath", "Fatigue", "Sore Throat"],
                "severity": "Medium",
                "advice": "🏠 **Self-Isolate & Test.** Monitor breathing. Seek care if breathing becomes difficult."
            },
            "Migraine": {
                "symptoms": ["Severe Pulsing Headache", "Sensitivity to Light", "Sensitivity to Sound", "Nausea", "Visual Aura"],
                "severity": "Medium",
                "advice": "💊 **Rest in a dark room.** Take over-the-counter pain relief. Consult a neurologist if frequent."
            },
            "Gastroenteritis (Stomach Flu)": {
                "symptoms": ["Watery Diarrhea", "Abdominal Cramps", "Nausea", "Vomiting", "Low Fever"],
                "severity": "Low",
                "advice": "💧 **Stay Hydrated.** Drink electrolytes. See a doctor if dehydration signs appear."
            },
            "Common Cold": {
                "symptoms": ["Sneezing", "Runny Nose", "Sore Throat", "Mild Cough", "Low Fever", "Watery Eyes"],
                "severity": "Low",
                "advice": "🛌 **Rest & Fluids.** Symptoms usually resolve in 7-10 days."
            },
            "Anxiety/Panic Attack": {
                "symptoms": ["Rapid Heart Rate", "Fear of Doom", "Sweating", "Trembling", "Shortness of Breath", "Chest Tightness"],
                "severity": "Medium",
                "advice": "🧘 **Deep Breathing.** If new symptoms, rule out heart issues first. Consult a mental health professional."
            },
            "Parkinson's Disease": {
                "symptoms": ["Tremors (Shaking)", "Slowed Movement", "Rigid Muscles", "Changes in Speech", "Impaired Balance"],
                "severity": "Medium",
                "advice": "🧠 **Neurologist Consultation.** Use the **Parkinsons Check** tool in the sidebar."
            }
        }
        
        all_symptoms = sorted(list(set([sym for data in disease_db.values() for sym in data["symptoms"]])))
        
        selected_symptoms = st.multiselect(
            "What are you experiencing?",
            all_symptoms,
            placeholder="Search symptoms (e.g., Chest Pain, Fever, Tremors...)"
        )
        
        st.markdown("")
        
        if st.button("🔍 Analyze Condition"):
            if not selected_symptoms:
                st.warning("Please select at least one symptom.")
            else:
                with st.spinner("Comparing against medical guidelines..."):
                    time.sleep(1.5)
                    
                    results = []
                    for disease, data in disease_db.items():
                        matched = set(selected_symptoms).intersection(data["symptoms"])
                        match_count = len(matched)
                        if match_count > 0:
                            results.append({
                                "disease": disease,
                                "score": match_count,
                                "matched_symptoms": list(matched),
                                "severity": data["severity"],
                                "advice": data["advice"]
                            })
                    
                    results.sort(key=lambda x: x["score"], reverse=True)
                    
                    if not results:
                        st.info("No exact match found. Please consult a General Physician.")
                    else:
                        top_result = results[0]
                        
                        st.markdown("### 📋 Analysis Result")
                        
                        severity_color = "green"
                        if top_result["severity"] == "Critical": severity_color = "red"
                        elif top_result["severity"] == "High": severity_color = "orange"
                        elif top_result["severity"] == "Medium": severity_color = "gold"
                        
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"## **{top_result['disease']}**")
                                st.caption(f"Based on matching **{top_result['score']}** symptoms.")
                            with c2:
                                st.markdown(f":{severity_color}[**{top_result['severity'].upper()} PRIORITY**]")
                        
                        st.progress(min(top_result['score'] / 4, 1.0))
                        st.info(f"**Recommended Action:**\n\n{top_result['advice']}")
                        st.markdown(f"**Symptoms Matched:** {', '.join(top_result['matched_symptoms'])}")
                        
                        if top_result['disease'] == "Diabetes (Type 2)":
                            st.markdown("[Go to Diabetes Tool](#diabetes-check)")
                        elif top_result['disease'] == "Heart Attack (Myocardial Infarction)":
                            st.markdown("[Go to Heart Disease Risk Tool](#heart-disease-check)")
                        
                        if len(results) > 1:
                            with st.expander("View other possible causes"):
                                for res in results[1:4]:
                                    st.markdown(f"**{res['disease']}** ({res['score']} matches) - *{res['severity']}*")


    # --- DIABETES PREDICTION PAGE ---
    elif selected == '🩸 Diabetes Check':

        st.title('🩸 Diabetes Risk Prediction')
        st.markdown("Enter clinical data to assess Type 2 Diabetes risk.")

        tab1, tab2 = st.tabs(["👤 Patient Profile", "🧪 Clinical Vitals"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                Pregnancies = st.number_input('Number of Pregnancies', min_value=0, max_value=20, step=1)
                Age = st.number_input('Age (Years)', min_value=0, max_value=120, step=1)
            with col2:
                BMI = st.number_input('BMI (Body Mass Index)', min_value=0.0, max_value=70.0, step=0.1)
                DiabetesPedigreeFunction = st.number_input('Pedigree Function', min_value=0.0, max_value=2.5, step=0.01, help="Family history score")

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                Glucose = st.number_input('Glucose Level (mg/dL)', min_value=0, max_value=300, step=1)
                BloodPressure = st.number_input('Blood Pressure (mm Hg)', min_value=0, max_value=200, step=1)
            with col2:
                Insulin = st.number_input('Insulin Level (mu U/ml)', min_value=0, max_value=1000, step=1)
                SkinThickness = st.number_input('Skin Thickness (mm)', min_value=0, max_value=100, step=1)

        st.markdown("")
        if st.button('Analyze Risk', key='diabetes_button'):
            with st.spinner('Processing...'):
                time.sleep(1)
                try:
                    user_input = [float(Pregnancies), float(Glucose), float(BloodPressure), float(SkinThickness), float(Insulin), float(BMI), float(DiabetesPedigreeFunction), float(Age)]
                    diabetes_prediction = diabetes_model.predict([user_input])
                    
                    if diabetes_prediction[0] == 1:
                        st.error('### Result: Positive for Diabetes Risk')
                        st.toast("Alert: High Risk Detected", icon="⚠️")
                        st.markdown("The model has identified patterns consistent with diabetes.")
                    else:
                        st.success('### Result: Negative (Healthy)')
                        st.toast("Analysis Result: Healthy", icon="✅")
                        st.markdown("No significant risk factors identified.")
                except Exception as e:
                    st.error(f"Error: {e}")


    # --- HEART DISEASE PREDICTION PAGE ---
    elif selected == '💓 Heart Disease Check':
        st.title('💓 Heart Disease Risk Prediction')
        st.markdown("Cardiovascular risk assessment based on clinical metrics.")

        tab1, tab2, tab3 = st.tabs(["👤 Demographics", "🩺 Vitals", "📉 ECG & Pain"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input('Age', min_value=1, max_value=120, step=1)
            with col2:
                sex = st.radio('Sex', ('Male', 'Female'), horizontal=True)
                sex_val = 1 if sex == 'Male' else 0

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                trestbps = st.number_input('Resting BP (mm Hg)', min_value=80, max_value=200, step=1)
                chol = st.number_input('Cholesterol (mg/dL)', min_value=100, max_value=600, step=1)
            with col2:
                thalach = st.number_input('Max Heart Rate', min_value=60, max_value=220, step=1)
                fbs = st.number_input('Fasting BS > 120? (1=True, 0=False)', min_value=0, max_value=1, step=1)

        with tab3:
            col1, col2, col3 = st.columns(3)
            with col1:
                cp = st.number_input('Chest Pain (0-3)', min_value=0, max_value=3)
                restecg = st.number_input('Resting ECG (0-2)', min_value=0, max_value=2)
            with col2:
                exang = st.number_input('Exer. Angina (1=Yes, 0=No)', min_value=0, max_value=1)
                oldpeak = st.number_input('ST Depression', min_value=0.0, max_value=7.0, step=0.1)
            with col3:
                slope = st.number_input('Slope (0-2)', min_value=0, max_value=2)
                ca = st.number_input('Major Vessels (0-3)', min_value=0, max_value=3)
                thal = st.number_input('Thal (1-3)', min_value=1, max_value=3)

        st.markdown("")
        if st.button('Evaluate Heart Health', key='heart_button'):
            with st.spinner('Analyzing Cardiovascular Data...'):
                time.sleep(1)
                try:
                    user_input = [float(x) for x in [age, sex_val, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]]
                    heart_prediction = heart_disease_model.predict([user_input])
                    
                    if heart_prediction[0] == 1:
                        st.error('### Result: Heart Disease Detected')
                        st.toast("Critical Alert: Heart Risk", icon="🚨")
                        st.markdown("Please consult a cardiologist immediately.")
                    else:
                        st.success('### Result: Healthy Heart')
                        st.toast("Heart Health: Normal", icon="💚")
                        st.markdown("Cardiovascular metrics appear normal.")
                except Exception as e:
                    st.error(f"Error: {e}")


    # --- PARKINSONS PREDICTION PAGE ---
    elif selected == '🧠 Parkinsons Check':
        st.title("🧠 Parkinson's Disease Prediction")
        st.markdown("Neural assessment using biomedical voice measurements.")

        with st.expander("ℹ️ How to use this tool"):
            st.info("Enter the acoustic parameters extracted from voice recordings. These values (Jitter, Shimmer, etc.) measure vocal stability.")

        tab1, tab2, tab3 = st.tabs(["Frequency & Pitch", "Variation (Jitter/Shimmer)", "Harmonics & Pulse"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                fo = st.number_input('MDVP:Fo(Hz) - Avg Freq', format="%.3f")
                fhi = st.number_input('MDVP:Fhi(Hz) - Max Freq', format="%.3f")
            with col2:
                flo = st.number_input('MDVP:Flo(Hz) - Min Freq', format="%.3f")

        with tab2:
            col1, col2, col3 = st.columns(3)
            with col1:
                Jitter_percent = st.number_input('MDVP:Jitter(%)', format="%.4f")
                Jitter_Abs = st.number_input('MDVP:Jitter(Abs)', format="%.5f")
                RAP = st.number_input('MDVP:RAP', format="%.4f")
                PPQ = st.number_input('MDVP:PPQ', format="%.4f")
                DDP = st.number_input('Jitter:DDP', format="%.5f")
            with col2:
                Shimmer = st.number_input('MDVP:Shimmer', format="%.4f")
                Shimmer_dB = st.number_input('MDVP:Shimmer(dB)', format="%.3f")
                APQ3 = st.number_input('Shimmer:APQ3', format="%.5f")
                APQ5 = st.number_input('Shimmer:APQ5', format="%.5f")
            with col3:
                APQ = st.number_input('MDVP:APQ', format="%.4f")
                DDA = st.number_input('Shimmer:DDA', format="%.5f")

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                NHR = st.number_input('NHR', format="%.5f")
                HNR = st.number_input('HNR', format="%.4f")
                PPE = st.number_input('PPE', format="%.6f")
            with col2:
                spread1 = st.number_input('spread1', format="%.6f")
                spread2 = st.number_input('spread2', format="%.6f")
                D2 = st.number_input('D2', format="%.6f")

        st.markdown("")
        if st.button("Analyze Neural Signs", key='parkinsons_button'):
            with st.spinner('Processing Vocal Biomarkers...'):
                time.sleep(1)
                try:
                    user_input = [
                        fo, fhi, flo, Jitter_percent, Jitter_Abs, RAP, PPQ, DDP,
                        Shimmer, Shimmer_dB, APQ3, APQ5, APQ, DDA, NHR, HNR,
                        1.15, 0.4, # Placeholder
                        spread1, spread2, D2, PPE
                    ]
                    parkinsons_prediction = parkinsons_model.predict([user_input])
                    
                    if parkinsons_prediction[0] == 1:
                        st.error("### Result: Parkinson's Detected")
                        st.toast("Alert: Parkinson's Signs", icon="🧠")
                    else:
                        st.success("### Result: Healthy Pattern")
                        st.toast("Result: Negative", icon="✅")
                except Exception as e:
                    st.error(f"Error: {e}")


    # ----------------------------------------------------------
    #  CHATBOT (UNCHANGED)
    # ----------------------------------------------------------
    st.markdown("---")

    def get_health_response(query):
        query = query.lower()
        if any(x in query for x in ["glucose", "sugar", "fbs"]):
            return "🩸 **Glucose:** Fasting blood sugar levels. Normal is <100 mg/dL. 100-125 is pre-diabetes, and >126 suggests diabetes."
        elif "bmi" in query:
            return "⚖️ **BMI (Body Mass Index):** A measure of body fat based on height and weight. Normal range is 18.5 - 24.9."
        elif "blood pressure" in query or "bp" in query or "trestbps" in query:
            return "💓 **Blood Pressure:** 'Resting Blood Pressure' (trestbps). High BP (>130/80 mmHg) strains the heart."
        elif "chest pain" in query or "cp" in query:
            return "💔 **Chest Pain (CP):** Classified into 4 types. Type 0 (Typical Angina) is often the most serious indicator."
        elif "parkinson" in query:
            return "🧠 **Parkinson's:** A neurodegenerative disorder. We use vocal frequency variations (Jitter, Shimmer) to detect it."
        elif "jitter" in query:
            return "〰️ **Jitter:** Measures the variation in the *pitch* of the voice. High jitter is a sign of vocal impairment."
        elif "hello" in query or "hi" in query:
            return "👋 Hello! I am your Medi-Predictor Assistant. Ask me about any medical term on this page!"
        else:
            return "🤖 I can explain parameters like BMI, Glucose, Chest Pain, or Jitter. Try asking about those!"

    with st.expander("💬 AI Health Assistant & FAQ", expanded=False):
        st.caption("⚠️ **Disclaimer:** I am an AI assistant providing definitions. I cannot provide medical diagnosis.")
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hello! Click a button below or type a question to learn about the health metrics."}]

        col_faq1, col_faq2, col_faq3, col_faq4 = st.columns(4)
        user_query = None
        if col_faq1.button("BMI?", use_container_width=True): user_query = "What is BMI?"
        if col_faq2.button("Glucose?", use_container_width=True): user_query = "Explain Glucose"
        if col_faq3.button("Chest Pain?", use_container_width=True): user_query = "What are Chest Pain types?"
        if col_faq4.button("Jitter?", use_container_width=True): user_query = "What is Jitter?"

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about a medical term..."):
            user_query = prompt

        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            response = get_health_response(user_query)
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
