import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="School Culture Typology Survey", layout="wide")

RESULTS_FILE = "anonymous_culture_results.csv"
SCHOOLS_FILE = "registered_schools.txt"
ADMIN_PASSWORD = "1234"

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
def load_schools():
    schools = {}
    if not os.path.exists(SCHOOLS_FILE):
        return schools
    with open(SCHOOLS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",", 1)
            if len(parts) == 2:
                schools[parts[0]] = parts[1]
            elif len(parts) == 1 and parts[0]:
                schools[parts[0]] = ""
    return schools

def save_school(code, name=""):
    with open(SCHOOLS_FILE, "a") as f:
        f.write(f"{code},{name}\n")

def clear_all_data():
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    if os.path.exists(SCHOOLS_FILE):
        os.remove(SCHOOLS_FILE)

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "login"
if "school_code" not in st.session_state:
    st.session_state.school_code = ""

# --- Render Functions ---
def render_login():
    st.markdown("<h1 style='text-align: center;'>Welcome</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter the 4-digit code provided by your school to take the survey.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Use a form to allow 'Enter' key submission
        with st.form("login_form"):
            code = st.text_input("4-digit school code", max_chars=4)
            submitted = st.form_submit_button("Enter", use_container_width=True)
            
            if submitted:
                if code == "0000":
                    st.session_state.page = "admin"
                st.rerun()
            elif code in load_schools():
                st.session_state.school_code = code
                st.session_state.school_name = load_schools()[code]
                st.session_state.page = "survey"
                st.rerun()
            else:
                st.error("This number is not correct. Please double-check with the person who sent you here to see what the four-digit code is that they would like you to use.")

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
            
            # Save to CSV
            results_df = pd.DataFrame([final_results])
            if not os.path.isfile(RESULTS_FILE):
                results_df.to_csv(RESULTS_FILE, index=False)
            else:
                results_df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)
                
            st.success("Thank you! Your response has been securely recorded.")
            st.balloons()
        else:
            st.error("Submission failed. Please scroll up and fix the categories that do not sum to exactly 10.")

def render_admin():
    col1, col2 = st.columns([8, 1])
    with col1:
        st.title("Admin Dashboard")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", key="admin_logout", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    
    st.header("School Results")
    
    if os.path.exists(RESULTS_FILE):
        try:
            df = pd.read_csv(RESULTS_FILE, dtype={"School Code": str})
            
            if "School Code" in df.columns and not df.empty:
                # Clean up the column for display
                df["School Code"] = df["School Code"].astype(str)
                schools = df["School Code"].unique()
                
                selected_school = st.selectbox("Select a School Code", schools)
                
                if selected_school:
                    school_df = df[df["School Code"] == selected_school]
                    
                    # Calculate averages
                    typology_names = list(typologies.values())
                    # Only average columns that exist
                    existing_cols = [col for col in typology_names if col in school_df.columns]
                    
                    if existing_cols:
                        avg_scores = school_df[existing_cols].mean().reset_index()
                        avg_scores.columns = ["Typology", "Average Score"]
                        
                        school_name_lookup = load_schools().get(selected_school, "")
                        display_title = f"Average Typology Distribution for {school_name_lookup} ({selected_school})" if school_name_lookup else f"Average Typology Distribution for School {selected_school}"
                        
                        st.markdown(f"<h3 style='text-align: center;'>{display_title}</h3>", unsafe_allow_html=True)
                        fig = px.pie(avg_scores, values="Average Score", names="Typology")
                        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        csv = school_df.to_csv(index=False)
                        col_dl1, col_dl2 = st.columns([4, 1])
                        with col_dl2:
                            st.download_button("Download CSV for this school", csv, f"school_{selected_school}_results.csv", "text/csv")
            else:
                st.info("The results file doesn't have School Code data yet.")
        except Exception as e:
            st.error("Error reading the results file. This usually happens if old survey data is mixed with the new format. Please use the 'Clear All Data' button below to reset.")
    else:
        st.info("No survey data available yet.")
        
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Admin Controls</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='text-align: center;'>Register a School</h3>", unsafe_allow_html=True)
        with st.form("register_form"):
            new_code = st.text_input("New 4-digit code", max_chars=4)
            school_name = st.text_input("School Name (Optional)")
            reg_password = st.text_input("Admin Password", type="password")
            submitted_reg = st.form_submit_button("Register School")
            
            if submitted_reg:
                if reg_password == ADMIN_PASSWORD:
                    if len(new_code) == 4 and new_code.isdigit():
                        if new_code not in load_schools():
                            save_school(new_code, school_name)
                            st.success(f"School code {new_code} registered successfully!")
                        else:
                            st.warning("This code is already registered.")
                    else:
                        st.error("Please enter a valid 4-digit numeric code.")
                else:
                    st.error("Incorrect password.")
                    
    with col2:
        st.markdown("<h3 style='text-align: center;'>Clear All Data</h3>", unsafe_allow_html=True)
        st.warning("This will permanently delete all survey results and registered school codes.")
        with st.form("clear_form"):
            clear_password = st.text_input("Admin Password", type="password")
            confirm = st.checkbox("I confirm I want to delete all data")
            submitted_clear = st.form_submit_button("Clear Data", type="primary")
            
            if submitted_clear:
                if clear_password == ADMIN_PASSWORD:
                    if confirm:
                        clear_all_data()
                        st.success("All data has been cleared successfully.")
                    else:
                        st.error("Please check the confirmation box.")
                else:
                    st.error("Incorrect password.")

# --- Router ---
if st.session_state.page == "login":
    render_login()
elif st.session_state.page == "survey":
    render_survey()
elif st.session_state.page == "admin":
    render_admin()