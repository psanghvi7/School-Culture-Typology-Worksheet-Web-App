# School Culture Typology Survey Web App

[![Streamlit App](https://static.streamlit.io/badge_hosted_sec.svg)](https://school-culture-typology-survey.streamlit.app/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source, mobile-friendly interactive web application built with **Streamlit** to administer, collect, and visualize the **School Culture Typology Survey**. 

This app allows schools to self-register, distribute surveys to their staff members via a simple 4-digit code, and access a real-time, interactive dashboard that visualizes their school's culture typology distribution.

> [!IMPORTANT]
> **Disclaimer**: This is a free, independent open-source tool. The creator of this repository has no ownership of the original School Culture Typology survey, nor any affiliation or relationship with the original authors. It is provided purely as a digital tool for educational and organizational improvement purposes.

---

## 🚀 Key Features

* **Self-Service Registration**: Schools can register in seconds, generating a custom 4-digit school code and a secure password.
* **Anonymous Survey Submission**: Staff members can submit responses anonymously using their school's 4-digit code.
* **Real-Time Data Visualization**: High-quality interactive dashboards featuring Plotly charts, percentage breakdowns, and respondent counts.
* **Hybrid Storage Architecture**:
  * **Local Mode**: Automatically falls back to offline CSV storage for easy local testing.
  * **Cloud Mode**: Connects to a Google Sheets database using a lightweight Google Apps Script API bridge to ensure 100% data persistence on ephemeral hosting platforms like Streamlit Cloud.
* **Keep-Awake Integration**: Built-in GitHub Actions scheduler that automatically pings the application periodically to prevent the container from entering idle sleep mode on free hosting plans.

---

## 📖 Walkthrough & Usage Guide

The application homepage contains a clean, tabbed interface designed for different user roles. Below is a walkthrough of the core functionality:

### 1. Registering a School
To start collecting data for your school, you must register it first:
1. Navigate to the **Register School** tab.
2. Enter your school's name.
3. Choose a custom password (you will use this password to view your school's survey results).
4. Click **Register School**.
5. The system will generate a unique **4-digit school code** (e.g., `0403`) and display your registration details. Copy these down!

### 2. Taking the Survey
Once a school is registered, the survey administrator shares the **4-digit school code** with their staff members.
1. Staff members open the app and go to the **Take Survey** tab.
2. Enter the school's **4-digit code** and click **Start Survey**.
3. Answer the survey questions by rating each statement according to how accurately it describes your school.
4. Click **Submit Survey**. All submissions are saved anonymously.

### 3. Viewing School Data & Results
Only individuals with the school's password can access the reports dashboard:
1. Go to the **View School Data** tab.
2. Enter your **4-digit school code** and your password.
3. Click **Login**.
4. The dashboard displays:
   * **Total Responses**: The number of staff members who have completed the survey.
   * **Typology Distribution Pie Chart**: Interactive breakdown of your school's culture (e.g., Toxic, Fragmented, Balkanized, Comfortable Collaboration, Contrived Collegiality, Collaborative).
   * **Detailed Scores**: A scrollable data table with individual anonymous responses to help you identify specific areas of strength or concern.
   * **Reset Data**: School owners have the ability to clear responses or delete their school registration directly from this dashboard.

---

## 🛠️ Developer Setup & Self-Hosting

If you want to host your own instance of this tool, modify the code, or add custom admin panels, you can fork this repository and host it for free.

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/School-Culture-Typology-Worksheet-Web-App.git
   cd School-Culture-Typology-Worksheet-Web-App
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App Locally**:
   ```bash
   streamlit run "Culture Typology Python App v1.py"
   ```
   *By default, the local app will run in offline mode, saving and loading data from `anonymous_culture_results.csv` and `schools_database.csv` in the root folder.*

---

## ☁️ Google Sheets Cloud Database Integration

Streamlit Community Cloud containers are ephemeral and reboot occasionally, which wipes local CSV files. To keep your data permanently, you can connect the app to a Google Sheet.

### Step-by-Step Setup:

1. **Create a Google Sheet**: Create a new, blank spreadsheet in your Google Drive.
2. **Open Apps Script**: Go to **Extensions > Apps Script** in the spreadsheet menu.
3. **Paste Code**: Delete any default code in the editor, and copy the contents of the [google_apps_script.js](file:///Users/macbook/Documents/Github/School-Culture-Typology-Worksheet-Web-App/google_apps_script.js) file from this repository.
4. **Deploy as Web App**:
   * Click **Deploy > New Deployment**.
   * Under *Select type*, click the gear icon and select **Web app**.
   * Set *Execute as* to **Me (your email)**.
   * Set *Who has access* to **Anyone**. (This allows the Streamlit app to communicate with it).
   * Click **Deploy**.
   * Copy the generated **Web App URL** (e.g., `https://script.google.com/macros/s/.../exec`).
5. **Configure Streamlit Secrets**:
   * **In Local Development**: Create a `.streamlit/secrets.toml` file in the project folder and paste:
     ```toml
     APPS_SCRIPT_URL = "https://script.google.com/macros/s/YOUR_DEPLOYED_URL_HERE/exec"
     ```
   * **In Production (Streamlit Cloud)**: Go to your App Settings -> **Secrets** page on the Streamlit dashboard, and paste the same configuration line.
6. Once configured, the application will automatically create the tables inside your Google Sheet and transition to `🟢 Connected` mode.

---

## ⚙️ Customizing System Administration

For security and privacy, the root system administration features are restricted behind an environment passcode. 
* To access the global database control panel, navigate to the **System Settings** tab on the homepage.
* The default admin passcode is set via the `ADMIN_PASSCODE` secret. If no secret is configured, it defaults to `admin123`.
* You can change this by adding `ADMIN_PASSCODE = "your_secure_password"` to your Streamlit secrets.
* In your own fork, you can customize or remove the system settings panel completely by editing [Culture Typology Python App v1.py](file:///Users/macbook/Documents/Github/School-Culture-Typology-Worksheet-Web-App/Culture%20Typology%20Python%20App%20v1.py).

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
