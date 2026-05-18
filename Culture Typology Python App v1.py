import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="School Culture Typology Survey", layout="wide")

st.title("School Culture Typology Survey")
st.markdown("""
**Anonymous Feedback:** This survey does not track your login, email, or IP address. 
For each category below, **distribute exactly 10 points** across the six statements based on how well they describe our school. 
If one statement is exactly accurate, assign 10 to that box; otherwise, distribute the 10 points (e.g., 5, 3, 2).
""")

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
# I've filled in the first 3 rows. Add Rows 4-12 following this pattern.
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
    }
    # Add Row 4 (Decision Making), Row 5 (Risk-Taking), etc. here...
}

RESULTS_FILE = "anonymous_culture_results.csv"

# Initialize dictionaries
user_scores = {col: 0 for col in typologies.keys()}
all_rows_valid = True

with st.form("culture_survey"):
    for category, statements in worksheet_data.items():
        st.subheader(category)
        st.markdown("---")
        
        row_total = 0
        row_inputs = {}
        
        # Display statements vertically for better readability
        for col_letter, text in statements.items():
            # Use columns to put the number input next to the text
            text_col, input_col = st.columns([4, 1])
            with text_col:
                st.write(text)
            with input_col:
                val = st.number_input(f"Points", min_value=0, max_value=10, value=0, key=f"{category}_{col_letter}", label_visibility="collapsed")
                row_inputs[col_letter] = val
                row_total += val
                
        st.write(f"**Current Total for {category}: {row_total}/10**")
        
        # Validation check
        if row_total != 10:
            st.error(f"⚠️ You must distribute exactly 10 points for {category}.")
            all_rows_valid = False
        else:
            # If valid, add to the user's running column totals
            for col_letter, val in row_inputs.items():
                user_scores[col_letter] += val
                
        st.markdown("<br><br>", unsafe_allow_html=True) # Spacing between major categories

    submitted = st.form_submit_button("Submit Anonymous Survey", type="primary")

    if submitted:
        if all_rows_valid:
            # Map the letter columns to their typology names for the final output
            final_results = {typologies[letter]: score for letter, score in user_scores.items()}
            final_results["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to CSV
            results_df = pd.DataFrame([final_results])
            if not os.path.isfile(RESULTS_FILE):
                results_df.to_csv(RESULTS_FILE, index=False)
            else:
                results_df.to_csv(RESULTS_FILE, mode='a', header=False, index=False)
                
            st.success("Thank you! Your response has been securely recorded.")
            st.balloons() # A little celebration animation upon success
        else:
            st.error("Submission failed. Please scroll up and fix the categories highlighted in red.")