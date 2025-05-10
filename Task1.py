import streamlit as st
import pandas as pd
import numpy as np
import time

# ✅ App Configuration (must be first Streamlit command)
st.set_page_config(page_title="Smart Water Monitoring", layout="wide")

# Dummy user database
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}  # username: password

# Session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Initialize simulation data
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Time", "pH", "Turbidity", "Temperature"])
if 'run_simulation' not in st.session_state:
    st.session_state.run_simulation = True

# ---------- Authentication functions ----------
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully!")
            #st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def signup():
    st.title("Sign Up")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    if st.button("Create Account"):
        if new_user in st.session_state.users:
            st.error("Username already exists.")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("Account created. Please log in.")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("You have been logged out.")
    #st.experimental_rerun()

# ---------- Main App ----------
def main_app():
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("💧 AI-Based Smart Water Quality and Distribution Monitoring (Simulated)")

    # Sidebar Controls
    with st.sidebar:
        st.header("⚙ Simulation Controls")
        if st.button("▶ Start" if not st.session_state.run_simulation else "⏸ Pause"):
            st.session_state.run_simulation = not st.session_state.run_simulation

        ph_limit = st.slider("Set pH Safe Range", 6.0, 9.0, (6.5, 8.5))
        turbidity_limit = st.slider("Max Turbidity (NTU)", 1.0, 10.0, 5.0)

        st.markdown("---")
        if st.download_button("📥 Download Data (CSV)", st.session_state.data.to_csv(index=False), "water_data.csv"):
            st.success("Download started")

    # Function to simulate new data
    def generate_data():
        now = pd.Timestamp.now()
        new_row = {
            "Time": now,
            "pH": round(np.random.normal(7, 0.2), 2),
            "Turbidity": round(np.random.normal(2.5, 0.5), 2),
            "Temperature": round(np.random.normal(25, 0.5), 2)
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)

    # Run simulation if active
    if st.session_state.run_simulation:
        generate_data()

    # Get latest data
    if not st.session_state.data.empty:
        latest = st.session_state.data.iloc[-1]
    else:
        latest = {"pH": 7, "Turbidity": 2.5, "Temperature": 25}

    # Display metrics and charts
    placeholder = st.empty()
    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("🧪 pH", latest["pH"])
        col2.metric("🌫 Turbidity (NTU)", latest["Turbidity"])
        col3.metric("🌡 Temperature (°C)", latest["Temperature"])

        st.markdown("### 📊 Live Water Quality Trends")
        st.line_chart(st.session_state.data.set_index("Time")[["pH", "Turbidity", "Temperature"]])

        # AI prediction logic
        status = "Safe"
        if latest["pH"] < ph_limit[0] or latest["pH"] > ph_limit[1] or latest["Turbidity"] > turbidity_limit:
            status = "Unsafe"

        st.markdown("### 🧠 AI Prediction")
        if status == "Safe":
            st.success("✅ Water Quality is Safe")
            st.image("https://th.bing.com/th/id/OIP.VGzOW7rGKnJB9D5_YhOIhAHaHZ?cb=iwp1&rs=1&pid=ImgDetMain.jpg",
                     caption="Safe Water", use_container_width=True)
        else:
            st.error("⚠ Water Quality is Unsafe")

        # Alert Section
        st.markdown("### 🚨 Real-Time Alerts")
        alerts = []
        if latest["pH"] < ph_limit[0] or latest["pH"] > ph_limit[1]:
            alerts.append("pH out of safe range!")
        if latest["Turbidity"] > turbidity_limit:
            alerts.append("High turbidity detected!")

        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.info("No active alerts.")
            st.image("https://www.shutterstock.com/shutterstock/photos/2076792079/display_1500/stock-vector-enable-alert-notification-vector-fill-outline-icon-design-illustration-web-and-mobile-application-2076792079.jpg",
                     caption="No Alerts", use_container_width=True)

    # Refresh every 2 seconds if running
    if st.session_state.run_simulation:
        time.sleep(2)
        #st.experimental_rerun()

# ---------- Page Navigation ----------
page = st.sidebar.radio("Navigation", ["Login", "Sign Up", "App"])

if not st.session_state.logged_in:
    if page == "Login":
        login()
    elif page == "Sign Up":
        signup()
    else:
        st.warning("Please log in to access the app.")
else:
    main_app()
