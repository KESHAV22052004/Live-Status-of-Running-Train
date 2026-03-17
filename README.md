# Indian Railways Live Status & Search Tool

A professional Python-based utility to fetch real-time train locations, schedules, and delays. 

## 🚀 Overview
This project demonstrates a robust implementation of data fetching from multiple sources with high resilience and fallback mechanisms. It uses **Object-Oriented Programming (OOP)** principles to separate concerns between data acquisition and visualization.

## ✨ Key Features
- **Smart Data Fetching**: Attempts to use RapidAPI for live delay data and falls back to `erail.in` for real schedule data if keys are missing or rejected (403).
- **Interactive Visualization**: Uses `Plotly` to generate dual-axis charts showing both arrival delays and journey distance progression.
- **Search Capability**: Allows searching for trains by name or number with automatic internal ID resolution.
- **Resilient Parsing**: Uses flexible parsing logic to handle dynamic changes in third-party data formats.

## 🛠️ Architecture
The project follows a modular design:
- **`IndianRailwaysClient`**: Handles API requests, session management, and raw data parsing (tilde/caret delimited formats).
- **`TrainVisualizer`**: A static utility class to handle data transformation and interactive plotting.
- **`main.py`**: A clean entry point for CLI interaction.

## 📦 Setup & Installation
1. **Clone the project** and navigate to the directory.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment** (Optional):
   Create a `.env` file and add your RapidAPI key for live delay data:
   ```text
   IRCTC_RAPIDAPI_KEY=your_key_here
   ```

## 🖥️ Usage
### CLI Mode
Run the script using Python:
```bash
python train_status.py
```

### Web Mode (Recommended for Interviews)
I have included a professional Web UI using **Streamlit**.
```bash
pip install streamlit
streamlit run app.py
```

## 🌐 Deployment
- **Git**: I have provided a [Deployment Guide](file:///C:/Users/RAGHAV/.gemini/antigravity/brain/9295ca7d-acab-4dd6-8c0d-5ae9aa4b6391/deployment_guide.md) for pushing to GitHub.
- **Hosting**: You can host the `app.py` on **Streamlit Cloud** for free (connect your GitHub repo).
- **Vercel**: If you prefer Vercel, use the Flask-based configuration (contact me if you need help with this).

## 💡 Interview Highlights
- **Error Handling**: Implements retry-logic and source-switching (RapidAPI -> erail.in).
- **Clean Code**: Adheres to SOLID principles and OOP.
- **Robustness**: Uses browser-like session simulation to overcome data scraping challenges.
