# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
# pyrefly: ignore [missing-import]
import plotly.express as px

st.set_page_config(page_title="School Culture Typology Survey", layout="wide")

# Center align tabs using custom CSS injection
st.markdown("""
    <style>
    [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

RESULTS_FILE = "anonymous_culture_results.csv"
SCHOOLS_FILE = "registered_schools.csv"

# Typology Mapping (for backend calculation)
typologies = {
    "A": "Toxic",
    "B": "Fragmented",
    "C": "Balkanized",
    "D": "Contrived Collegiality",
    "E": "Comfortable Collaboration",
    "F": "Collaborative"
}

# The Worksheet Data Structure
worksheet_data = {
    "1. Student Achievement": {
        "A": "Many teachers believe that if students fail it is the students fault.",
        "B": "Teachers usually do not discuss issues related to student achievement.",
        "C": "Most teacher discussions related to student achievement are restricted to within departments, cliques, or close friends.",
        "D": "Teachers are given time to discuss student achievement and are expected to do that during this time.",
        "E": "Teachers are given time to discuss student achievement but most of this time is spent on giving advice and trick-trading.",
        "F": "Teachers are given time to discuss student achievement and this time is spent critically analyzing each others' practice."
    },
    "2. Collegial Awareness": {
        "A": "Many teachers do not care about the effectiveness of other teachers.",
        "B": "Most of the teachers are unaware of what other teachers are teaching.",
        "C": "Most teachers are aware of only what their friends in the school are teaching.",
        "D": "The school leadership expects teachers to know what the other teachers are teaching.",
        "E": "Teachers occasionally observe and discuss what other teachers are teaching.",
        "F": "Teachers seek out opportunities to observe and discuss what other teachers are teaching."
    },
    "3. Shared Values": {
        "A": "Values shared by many teachers are contradictory with student needs.",
        "B": "There is not much agreement among teachers concerning ed. values.",
        "C": "There are small groups of teachers that share educational values.",
        "D": "The school leadership provides teachers a list of school values.",
        "E": "There is general agreement among teachers concerning educational values.",
        "F": "There is strong agreement among teachers concerning educational values."
    },
    "4. Decision Making": {
        "A": "Decisions are easily made because many teachers do not care.",
        "B": "Teachers are usually not interested in participating in decisions that concern students.",
        "C": "There are small groups of teachers that attempt to control the decisions made concerning students.",
        "D": "School leaders expect teachers to participate in all decisions concerning students.",
        "E": "Teachers occasionally show an interest in the decisions made concerning students.",
        "F": "There is an expectation among teachers to participate in decisions concerning students."
    },
    "5. Risk-Taking": {
        "A": "Many teachers protect their teaching style from 'innovation'.",
        "B": "Most teachers typically do not experiment with new ideas.",
        "C": "Innovations are usually initiated within a single grade or department.",
        "D": "School leaders mandate teachers to try new ideas.",
        "E": "Teachers occasionally like to experiment with new ideas.",
        "F": "Teachers are constantly looking for new ideas."
    },
    "6. Trust": {
        "A": "Teachers talk behind other teachers' backs.",
        "B": "Trust among teachers is not considered necessary.",
        "C": "There are teachers who only trust certain teachers.",
        "D": "Teachers are placed in situations where they are required to trust each other.",
        "E": "Trust is assumed and therefore not a critical issue.",
        "F": "There is a strong interdependence among teachers at this school."
    },
    "7. Openness": {
        "A": "Teachers who are committed to students and to learning are subject to criticism.",
        "B": "Teachers usually are not interested in suggestions concerning instruction made by other teachers.",
        "C": "Teachers usually keep their opinions and advice concerning instruction among their friends.",
        "D": "Teachers are expected to contribute to discussions about effective teaching at meetings.",
        "E": "Teachers are occasionally open to giving or receiving advice concerning instruction.",
        "F": "Teachers are very interested in the opinions of their colleagues concerning instruction."
    },
    "8. Parent Relations": {
        "A": "Many teachers avoid parents whenever possible.",
        "B": "Teachers would rather not have parents' input regarding instructional practice.",
        "C": "There are cliques of teachers that parents perceive as the better teachers.",
        "D": "School leaders require teachers to be in contact with parents regularly.",
        "E": "Most teachers are comfortable when parents want to be involved with instructional practices.",
        "F": "Teachers aggressively seek the involvement of parents in classroom instruction."
    },
    "9. Leadership": {
        "A": "School leaders are seen as obstacles to growth and development.",
        "B": "School leaders are not visible in the school very much.",
        "C": "School leaders frequently visit and/or praise the same teachers.",
        "D": "School leaders monitor the meetings that are designed for teacher collaboration.",
        "E": "School leaders encourage teachers to give each other advice without being too critical.",
        "F": "School leaders challenge ineffective teaching and encourage teachers to do the same."
    },
    "10. Communication": {
        "A": "School policies seem to inhibit teachers' abilities to discuss student achievement.",
        "B": "Communication among teachers is not considered important at this school.",
        "C": "It is difficult to have productive dialogue with certain groups of teachers.",
        "D": "Communication is dominated by top-down mandates.",
        "E": "Warm and fuzzy conversations permeate our school.",
        "F": "Any teacher can talk to any teacher about their teaching practice."
    },
    "11. Socialization": {
        "A": "New teachers are informally indoctrinated by negative staff members quickly.",
        "B": "Teachers at this school quickly learn that it is 'every man for himself'.",
        "C": "New teachers are informally labeled, then typecast into certain teacher cliques.",
        "D": "There are many mandatory meetings for new teachers to attend.",
        "E": "New teachers are encouraged to share their experiences with other faculty members.",
        "F": "All teachers assume some responsibility in helping new teachers adjust."
    },
    "12. Organization History": {
        "A": "Teachers are quick to share negative stories about this school.",
        "B": "'Teachers asking for help' has traditionally been considered as a professional weakness.",
        "C": "Some grades, departments, or teams consider their successes as separate from the whole school.",
        "D": "School leaders have established strong control over much of what goes on at school.",
        "E": "This school is known for celebrating everything.",
        "F": "At this school there is an understanding that school improvement is a continuous issue."
    }
}

# --- Helper Functions ---
def get_apps_script_url():
    try:
        return st.secrets.get("APPS_SCRIPT_URL")
    except Exception:
        return os.environ.get("APPS_SCRIPT_URL")

def get_api_key():
    try:
        return st.secrets.get("APPS_SCRIPT_API_KEY", "")
    except Exception:
        return os.environ.get("APPS_SCRIPT_API_KEY", "")

def post_to_apps_script(url, payload):
    # Google Apps Script handles POST requests by storing the payload and returning a 302 redirect.
    # The client must follow the redirect as a GET request to trigger script execution on the sandbox.
    # Standard requests.post() handles this sequence automatically.
    return requests.post(url, json=payload, timeout=10)

def load_schools_raw():
    url = get_apps_script_url()
    if url:
        try:
            r = requests.get(f"{url}?action=get_schools&api_key={get_api_key()}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and "error" in data:
                    st.error(f"Google Sheets Error: {data['error']}")
                    return pd.DataFrame(columns=["school_code", "school_name", "password"])
                df = pd.DataFrame(data)
                if df.empty:
                    return pd.DataFrame(columns=["school_code", "school_name", "password"])
                df["school_code"] = df["school_code"].astype(str).str.zfill(4)
                df["password"] = df["password"].astype(str)
                return df
        except Exception as e:
            st.error(f"Error loading schools from Google Sheets: {e}")
            return pd.DataFrame(columns=["school_code", "school_name", "password"])

    if not os.path.exists(SCHOOLS_FILE):
        return pd.DataFrame(columns=["school_code", "school_name", "password"])
    try:
        df = pd.read_csv(SCHOOLS_FILE, dtype={"school_code": str, "password": str})
        if not df.empty:
            df["school_code"] = df["school_code"].astype(str).str.zfill(4)
        return df
    except Exception:
        return pd.DataFrame(columns=["school_code", "school_name", "password"])

def load_schools():
    df = load_schools_raw()
    return dict(zip(df["school_code"].astype(str), df["school_name"].fillna("")))

def load_school_passwords():
    df = load_schools_raw()
    return dict(zip(df["school_code"].astype(str), df["password"].fillna("")))

def save_school(code, name, password):
    url = get_apps_script_url()
    if url:
        payload = {
            "action": "save_school",
            "api_key": get_api_key(),
            "school_code": str(code),
            "school_name": name,
            "password": str(password)
        }
        try:
            r = post_to_apps_script(url, payload)
            if r.status_code == 200:
                return True
            else:
                st.error(f"Google Sheets returned status code {r.status_code}")
                return False
        except Exception as e:
            st.error(f"Error saving school to Google Sheets: {e}")
            return False

    df = load_schools_raw()
    new_school = pd.DataFrame([{"school_code": str(code), "school_name": name, "password": str(password)}])
    df = pd.concat([df, new_school], ignore_index=True)
    df.to_csv(SCHOOLS_FILE, index=False)
    return True

def load_results_raw():
    url = get_apps_script_url()
    if url:
        try:
            r = requests.get(f"{url}?action=get_results&api_key={get_api_key()}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and "error" in data:
                    st.error(f"Google Sheets Error: {data['error']}")
                    return pd.DataFrame(columns=[
                        "Timestamp", "School Code", "Toxic", "Fragmented", "Balkanized", 
                        "Contrived Collegiality", "Comfortable Collaboration", "Collaborative"
                    ])
                df = pd.DataFrame(data)
                if df.empty:
                    return pd.DataFrame(columns=[
                        "Timestamp", "School Code", "Toxic", "Fragmented", "Balkanized", 
                        "Contrived Collegiality", "Comfortable Collaboration", "Collaborative"
                    ])
                df["School Code"] = df["School Code"].astype(str).str.zfill(4)
                return df
        except Exception as e:
            st.error(f"Error loading results from Google Sheets: {e}")
            return pd.DataFrame(columns=[
                "Timestamp", "School Code", "Toxic", "Fragmented", "Balkanized", 
                "Contrived Collegiality", "Comfortable Collaboration", "Collaborative"
            ])

    if not os.path.exists(RESULTS_FILE):
        return pd.DataFrame(columns=[
            "Timestamp", "School Code", "Toxic", "Fragmented", "Balkanized", 
            "Contrived Collegiality", "Comfortable Collaboration", "Collaborative"
        ])
    try:
        df = pd.read_csv(RESULTS_FILE, dtype={"School Code": str})
        if not df.empty:
            df["School Code"] = df["School Code"].astype(str).str.zfill(4)
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "Timestamp", "School Code", "Toxic", "Fragmented", "Balkanized", 
            "Contrived Collegiality", "Comfortable Collaboration", "Collaborative"
        ])

def save_result(final_results):
    url = get_apps_script_url()
    if url:
        payload = {
            "action": "save_result",
            "api_key": get_api_key(),
            "Timestamp": final_results["Timestamp"],
            "School Code": final_results["School Code"],
            "Toxic": int(final_results.get("Toxic", 0)),
            "Fragmented": int(final_results.get("Fragmented", 0)),
            "Balkanized": int(final_results.get("Balkanized", 0)),
            "Contrived Collegiality": int(final_results.get("Contrived Collegiality", 0)),
            "Comfortable Collaboration": int(final_results.get("Comfortable Collaboration", 0)),
            "Collaborative": int(final_results.get("Collaborative", 0))
        }
        try:
            r = post_to_apps_script(url, payload)
            if r.status_code == 200:
                return True
            else:
                st.error(f"Google Sheets returned status code {r.status_code}")
                return False
        except Exception as e:
            st.error(f"Error saving result to Google Sheets: {e}")
            return False

    try:
        results_df = pd.DataFrame([final_results])
        if not os.path.isfile(RESULTS_FILE):
            results_df.to_csv(RESULTS_FILE, index=False)
        else:
            results_df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)
        return True
    except Exception:
        return False

def clear_school_data(school_code):
    url = get_apps_script_url()
    if url:
        payload = {
            "action": "clear_school_data",
            "api_key": get_api_key(),
            "school_code": str(school_code)
        }
        try:
            r = post_to_apps_script(url, payload)
            if r.status_code == 200:
                return True
            else:
                st.error(f"Google Sheets returned status code {r.status_code}")
                return False
        except Exception as e:
            st.error(f"Error clearing school data in Google Sheets: {e}")
            return False

    if os.path.exists(RESULTS_FILE):
        try:
            df = pd.read_csv(RESULTS_FILE, dtype={"School Code": str})
            df["School Code"] = df["School Code"].astype(str)
            df_filtered = df[df["School Code"] != str(school_code)]
            df_filtered.to_csv(RESULTS_FILE, index=False)
            return True
        except Exception:
            return False
    return False

def delete_school_registration(school_code):
    url = get_apps_script_url()
    if url:
        payload = {
            "action": "delete_school_registration",
            "api_key": get_api_key(),
            "school_code": str(school_code)
        }
        try:
            r = post_to_apps_script(url, payload)
            if r.status_code == 200:
                return True
            else:
                st.error(f"Google Sheets returned status code {r.status_code}")
                return False
        except Exception as e:
            st.error(f"Error deleting school registration in Google Sheets: {e}")
            return False

    try:
        df = load_schools_raw()
        df = df[df["school_code"] != str(school_code)]
        df.to_csv(SCHOOLS_FILE, index=False)
        return True
    except Exception:
        return False

def clear_all_data():
    url = get_apps_script_url()
    if url:
        payload = {
            "action": "clear_all_data",
            "api_key": get_api_key()
        }
        try:
            r = post_to_apps_script(url, payload)
            if r.status_code == 200:
                return True
            else:
                st.error(f"Google Sheets returned status code {r.status_code}")
                return False
        except Exception as e:
            st.error(f"Error clearing all data in Google Sheets: {e}")
            return False

    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    if os.path.exists(SCHOOLS_FILE):
        os.remove(SCHOOLS_FILE)
    return True

def verify_admin_password(password_input):
    import hashlib
    env_pass = os.environ.get("SUPER_ADMIN_PASSWORD")
    if env_pass:
        return password_input == env_pass
    target_hash = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4"
    return hashlib.sha256(password_input.encode()).hexdigest() == target_hash

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "login"
if "school_code" not in st.session_state:
    st.session_state.school_code = ""

# --- Render Functions ---
def render_login():
    st.markdown("<h1 style='text-align: center;'>Welcome!</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        tab1, tab2, tab3, tab4 = st.tabs([
            "Take Survey", 
            "View School Data", 
            "Register School", 
            "System Settings"
        ])
        
        with tab1:
            st.markdown("<p style='margin-top: 1rem;'>Enter the 4-digit code provided by your school to begin the survey.</p>", unsafe_allow_html=True)
            with st.form("take_survey_form"):
                st.markdown(
                    """
                    <div style="
                        background-color: var(--secondary-background-color);
                        border: 1px solid rgba(128, 128, 128, 0.15);
                        border-radius: 8px;
                        padding: 14px 18px;
                        margin-bottom: 20px;
                    ">
                        <div style="font-size: 0.88em; color: var(--text-color); line-height: 1.4; margin-bottom: 12px;">
                            <strong>Duration:</strong> The entire survey consists of 12 categories and takes approximately 5 to 10 minutes to complete.
                        </div>
                        <div style="font-size: 0.88em; color: var(--text-color); line-height: 1.4;">
                            <strong>Privacy & Anonymity:</strong> Administered solely for graduate academic research in transformational educational leadership. This platform does not track logins, IP addresses, or browser data; only the points you submit are securely collected.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                code = st.text_input("4-digit school code", max_chars=4, key="survey_code_input")
                submitted = st.form_submit_button("Start Survey", use_container_width=True)
                
                if submitted:
                    if code == "0000":
                        st.warning("Please use the 'System Settings' tab to log in.")
                    elif code in load_schools():
                        st.session_state.school_code = code
                        st.session_state.school_name = load_schools()[code]
                        st.session_state.page = "survey"
                        st.rerun()
                    else:
                        st.error("This number is not correct. Please double-check with the person who sent you here to see what the four-digit code is that they would like you to use.")
        
        with tab2:
            st.markdown("<p style='margin-top: 1rem;'>Log in to view your school's survey responses and data analysis.</p>", unsafe_allow_html=True)
            with st.form("view_data_form"):
                code = st.text_input("4-digit school code", max_chars=4, key="dashboard_code_input")
                password = st.text_input("Password", type="password", key="dashboard_password_input")
                submitted = st.form_submit_button("View Data Dashboard", use_container_width=True)
                
                if submitted:
                    school_passwords = load_school_passwords()
                    if code in load_schools() and password == school_passwords.get(code, ""):
                        st.session_state.dashboard_school_code = code
                        st.session_state.school_name = load_schools()[code]
                        st.session_state.page = "school_dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid school code or password. Please try again.")
                        
        with tab3:
            st.markdown("<p style='margin-top: 1rem;'>Register a new school code to distribute to your staff and collect survey responses.</p>", unsafe_allow_html=True)
            with st.form("register_school_form"):
                new_code = st.text_input("Create 4-digit school code", max_chars=4, key="register_code_input")
                school_name = st.text_input("School Name (Optional)", key="register_name_input")
                new_password = st.text_input("Create Dashboard Password", type="password", key="register_password_input")
                submitted = st.form_submit_button("Register School", use_container_width=True)
                
                if submitted:
                    if len(new_code) == 4 and new_code.isdigit():
                        if new_code == "0000":
                            st.error("Code '0000' is reserved for system administration. Please choose another code.")
                        elif new_code not in load_schools():
                            if new_password.strip():
                                if save_school(new_code, school_name, new_password):
                                    st.success(f"School {new_code} registered successfully! You can now share this code with your staff, and log in to the 'View School Data' tab using your password.")
                                else:
                                    st.error("Failed to register school code. Please check the connection error above.")
                            else:
                                st.error("Please create a password for reviewing your data.")
                        else:
                            st.warning("This school code is already registered. Please choose another 4-digit code.")
                    else:
                        st.error("Please enter a valid 4-digit numeric code.")
                        
        with tab4:
            st.markdown("<p style='margin-top: 1rem;'>System Settings Portal</p>", unsafe_allow_html=True)
            with st.form("super_admin_form"):
                admin_pass = st.text_input("Enter Admin Password", type="password", key="admin_password_input")
                submitted = st.form_submit_button("Log In to System Settings", use_container_width=True)
                
                if submitted:
                    if verify_admin_password(admin_pass):
                        st.session_state.page = "admin"
                        st.rerun()
                    else:
                        st.error("Incorrect admin password.")
 
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 0.85em; color: #666;'>"
        "The text and structure of this survey are the intellectual property of Steve Gruenert and Jerry Valentine (MLLC, 2000; rev. 2006). "
        "This digital application was built independently to facilitate the anonymous administration and data collection of their worksheet for academic analysis. "
        "The developer of this application is not affiliated with the original authors."
        "</p>", 
        unsafe_allow_html=True
    )

def render_survey():
    school_name = st.session_state.get("school_name", "")
    if school_name:
        st.markdown(f"<h1 style='text-align: center;'>Survey for {school_name}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-style: italic;'>If this is not correct, please ensure that you typed in the correct code.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center;'>School Culture Typology Survey</h1>", unsafe_allow_html=True)
    
    st.markdown(f"**School Code:** {st.session_state.school_code}")
            
    st.markdown("""
    **Anonymous Feedback:** This survey does not track your login, email, or IP address. 
    For each category below, **distribute exactly 10 points** across the six statements based on how well they describe your school. 
    If one statement is exactly accurate, assign 10 to that box; otherwise, distribute the 10 points (e.g., 5, 3, 2).
    """)

    # Initialize dictionaries
    user_scores = {col: 0 for col in typologies.keys()}
    all_rows_valid = True

    for category, statements in worksheet_data.items():
        st.subheader(category)
        st.markdown("---")
        
        row_total = 0
        row_inputs = {}
        
        # Display statements vertically for better readability
        for col_letter, text in statements.items():
            text_col, input_col = st.columns([4, 1])
            with text_col:
                st.write(text)
            with input_col:
                val = st.number_input(f"Points", min_value=0, max_value=10, value=0, key=f"{category}_{col_letter}", label_visibility="collapsed")
                row_inputs[col_letter] = val
                row_total += val
                
        # Validation check and dynamic total display
        if row_total != 10:
            st.markdown(f"**<span style='color:red'>Current Total for {category}: {row_total}/10</span>** (You must distribute exactly 10 points)", unsafe_allow_html=True)
            all_rows_valid = False
        else:
            st.markdown(f"**<span style='color:green'>Current Total for {category}: 10/10</span>** ✅", unsafe_allow_html=True)
            for col_letter, val in row_inputs.items():
                user_scores[col_letter] += val
                
        st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; color: #856404; background-color: #fff3cd; padding: 16px; border-radius: 0.25rem; margin-bottom: 1rem; border: 1px solid #ffeeba;'>Make sure to submit your survey before logging out, as unsaved data will be lost.</div>", unsafe_allow_html=True)
        submitted = st.button("Submit Anonymous Survey", type="primary", use_container_width=True)
        if st.button("Logout", key="logout_survey", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.school_code = ""
            st.rerun()

    if submitted:
        if all_rows_valid:
            final_results = {typologies[letter]: score for letter, score in user_scores.items()}
            final_results["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            final_results["School Code"] = st.session_state.school_code
            
            # Save to database (Google Sheets or local CSV fallback)
            if save_result(final_results):
                st.success("Thank you! Your response has been securely recorded.")
                st.balloons()
            else:
                st.error("Error saving your response. Please try again.")
        else:
            st.error("Submission failed. Please scroll up and fix the categories that do not sum to exactly 10.")

def render_school_dashboard():
    school_code = st.session_state.get("dashboard_school_code", "")
    school_name = st.session_state.get("school_name", "")
    
    col1, col2 = st.columns([8, 1])
    with col1:
        display_title = f"Data Dashboard: {school_name} ({school_code})" if school_name else f"Data Dashboard: School {school_code}"
        st.title(display_title)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", key="dashboard_logout", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.dashboard_school_code = ""
            st.session_state.school_name = ""
            st.rerun()
            
    st.header("School Survey Results")
    
    try:
        df = load_results_raw()
        school_df = df[df["School Code"] == str(school_code)] if not df.empty else pd.DataFrame()
        
        if not school_df.empty:
            # Calculate averages
            typology_names = list(typologies.values())
            existing_cols = [col for col in typology_names if col in school_df.columns]
            
            if existing_cols:
                avg_scores = school_df[existing_cols].mean().reset_index()
                avg_scores.columns = ["Typology", "Average Score"]
                
                st.markdown("<h3 style='text-align: center;'>Average Typology Distribution</h3>", unsafe_allow_html=True)
                fig = px.pie(avg_scores, values="Average Score", names="Typology")
                fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)
                
                # Download CSV for this school
                csv = school_df.to_csv(index=False)
                col_dl1, col_dl2 = st.columns([4, 1])
                with col_dl2:
                    st.download_button("Download CSV for this school", csv, f"school_{school_code}_results.csv", "text/csv", use_container_width=True)
        else:
            st.info("No survey responses recorded for this school yet.")
    except Exception as e:
        st.error(f"Error reading results: {e}")
        
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: red;'>Danger Zone</h2>", unsafe_allow_html=True)
    
    col_dmg1, col_dmg2 = st.columns([1, 1])
    with col_dmg1:
        st.markdown("<h3>Clear School Data</h3>", unsafe_allow_html=True)
        st.write("This will permanently delete all survey submissions for this school. This action cannot be undone.")
    with col_dmg2:
        with st.form("clear_school_form"):
            password_input = st.text_input("Enter School Dashboard Password to Confirm", type="password")
            confirm = st.checkbox("I confirm that I want to permanently delete all survey data for this school.")
            submitted_clear = st.form_submit_button("Clear All School Data", type="primary")
            
            if submitted_clear:
                school_passwords = load_school_passwords()
                actual_password = school_passwords.get(school_code, "")
                
                if password_input == actual_password:
                    if confirm:
                        if clear_school_data(school_code):
                            st.success("School data cleared successfully!")
                            st.rerun()
                        else:
                            st.warning("No data was found to clear, or an error occurred.")
                    else:
                        st.error("Please check the confirmation box.")
                else:
                    st.error("Incorrect password.")

def render_admin():
    col1, col2 = st.columns([8, 1])
    with col1:
        st.title("System Settings Dashboard")
        if get_apps_script_url():
            st.markdown("<p style='color: green; font-size: 0.9em; font-weight: bold; margin-top: -10px;'>🟢 Database Status: Connected to Google Sheets</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color: orange; font-size: 0.9em; font-weight: bold; margin-top: -10px;'>⚪ Database Status: Local CSV Fallback Mode (Offline)</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", key="admin_logout", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
            
    tab_data, tab_control = st.tabs(["School Data & Passwords", "System Administration"])
    
    with tab_data:
        col_list, col_chart = st.columns([1, 1])
        
        with col_list:
            st.subheader("Registered Schools & Passwords")
            df_schools = load_schools_raw()
            if not df_schools.empty:
                # Rename columns for friendly display
                df_display = df_schools.rename(columns={
                    "school_code": "School Code",
                    "school_name": "School Name",
                    "password": "Password"
                })
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No schools registered yet.")
                
        with col_chart:
            st.subheader("View School Data")
            try:
                df_results = load_results_raw()
                if not df_results.empty:
                    schools_with_data = df_results["School Code"].unique()
                    selected_school = st.selectbox("Select School Code to View", schools_with_data)
                    
                    if selected_school:
                        school_df = df_results[df_results["School Code"] == selected_school]
                        
                        # Calculate averages
                        typology_names = list(typologies.values())
                        existing_cols = [col for col in typology_names if col in school_df.columns]
                        
                        if existing_cols:
                            avg_scores = school_df[existing_cols].mean().reset_index()
                            avg_scores.columns = ["Typology", "Average Score"]
                            
                            school_name_lookup = load_schools().get(selected_school, "")
                            display_title = f"Average Typology Distribution for {school_name_lookup} ({selected_school})" if school_name_lookup else f"Average Typology Distribution for School {selected_school}"
                            
                            st.markdown(f"<h4 style='text-align: center;'>{display_title}</h4>", unsafe_allow_html=True)
                            fig = px.pie(avg_scores, values="Average Score", names="Typology")
                            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                            st.plotly_chart(fig, use_container_width=True)
                            
                            csv = school_df.to_csv(index=False)
                            st.download_button("Download CSV for this school", csv, f"school_{selected_school}_results.csv", "text/csv", use_container_width=True)
                else:
                    st.info("No survey results recorded yet.")
            except Exception as e:
                st.error(f"Error reading survey results: {e}")
                
    with tab_control:
        st.subheader("Data Management & Deletion")
        
        col_del_school, col_del_all = st.columns(2)
        
        with col_del_school:
            st.markdown("<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffeeba;'><strong>Delete Specific School</strong><br>Remove a specific school's survey responses and/or its registration record.</div>", unsafe_allow_html=True)
            
            # List all registered schools for deletion
            schools_list = list(load_schools().keys())
            
            with st.form("delete_school_form"):
                school_to_delete = st.selectbox("Select School Code", schools_list if schools_list else ["No schools registered"])
                delete_reg = st.checkbox("Also delete school registration (removes password & code)")
                pass_confirm = st.text_input("Enter Admin Password", type="password", key="del_school_admin_pass")
                confirm_check = st.checkbox("I confirm I want to permanently delete this data.")
                submit_del_school = st.form_submit_button("Delete School Data", type="primary")
                
                if submit_del_school:
                    if school_to_delete == "No schools registered":
                        st.error("No schools registered to delete.")
                    elif verify_admin_password(pass_confirm):
                        if confirm_check:
                            success = clear_school_data(school_to_delete)
                            if delete_reg:
                                success = success and delete_school_registration(school_to_delete)
                            
                            if success:
                                if delete_reg:
                                    st.success(f"School {school_to_delete} survey data and registration record deleted successfully.")
                                else:
                                    st.success(f"School {school_to_delete} survey data cleared successfully.")
                                st.rerun()
                            else:
                                st.error("Failed to complete deletion in the database. Please check the error above.")
                        else:
                            st.error("Please check the confirmation box.")
                    else:
                        st.error("Incorrect admin password.")
                        
        with col_del_all:
            st.markdown("<div style='background-color: #f8d7da; padding: 15px; border-radius: 5px; border: 1px solid #f5c6cb;'><strong>Reset System (Delete All)</strong><br>Permanently delete all registered schools, passwords, and survey results.</div>", unsafe_allow_html=True)
            
            with st.form("clear_all_form"):
                pass_confirm_all = st.text_input("Enter Admin Password", type="password", key="clear_all_admin_pass")
                confirm_check_all = st.checkbox("I confirm I want to wipe all system data. THIS CANNOT BE UNDONE.")
                submit_clear_all = st.form_submit_button("Wipe All Data", type="primary")
                
                if submit_clear_all:
                    if verify_admin_password(pass_confirm_all):
                        if confirm_check_all:
                            if clear_all_data():
                                st.success("All system data has been wiped successfully.")
                                st.rerun()
                            else:
                                st.error("Failed to wipe system data. Please check the error above.")
                        else:
                            st.error("Please check the confirmation box.")
                    else:
                        st.error("Incorrect admin password.")

# --- Router ---
if st.session_state.page == "login":
    render_login()
elif st.session_state.page == "survey":
    render_survey()
elif st.session_state.page == "school_dashboard":
    render_school_dashboard()
elif st.session_state.page == "admin":
    render_admin()