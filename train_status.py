import os
import re
import requests
import pandas as pd
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class IndianRailwaysClient:
    """Handles data fetching from IRCTC/erail.in with robust fallbacks."""
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://erail.in/",
        "Accept": "*/*"
    }

    def __init__(self, rapidapi_key=None):
        self.rapidapi_key = rapidapi_key
        self.session = requests.Session()
        # Initialize session with home page to get cookies
        try:
            self.session.get("https://erail.in", headers=self.HEADERS, timeout=5)
        except:
            pass

    def search_trains(self, query):
        """Searches trains by name or number."""
        try:
            url = "https://erail.in/rail/getTrains.aspx"
        # DataSource=2 is more reliable for name-based search as well
            params = {"TrainNo": query, "DataSource": "2", "Language": "0", "Cache": "true"}
            resp = self.session.get(url, params=params, headers=self.HEADERS, timeout=10)
            return self._parse_train_list(resp.text)
        except Exception as e:
            print(f"[!] Search Error: {e}")
            return []

    def get_live_status(self, train_no):
        """Orchestrates live status fetch with RapidAPI -> erail.in fallback."""
        if self.rapidapi_key and self.rapidapi_key != "your_api_key_here":
            print(f"[*] Attempting RapidAPI live fetch for {train_no}...")
            status = self._fetch_rapidapi_status(train_no)
            if status: return {"source": "live", "data": status}

        print("[*] Falling back to erail.in schedule data...")
        schedule = self._fetch_erail_schedule(train_no)
        if schedule: return {"source": "schedule", "data": schedule}
        
        return None

    def _fetch_rapidapi_status(self, train_no):
        """Fetches real-time delay data from RapidAPI."""
        try:
            url = "https://irctc1.p.rapidapi.com/api/v1/liveTrainStatus"
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "irctc1.p.rapidapi.com"
            }
            resp = requests.get(url, headers=headers, params={"trainNo": train_no, "startDay": "1"}, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("data")
        except: return None
        return None

    def _fetch_erail_schedule(self, train_no):
        """Fetches full route schedule using erail.in TRAINROUTE endpoint."""
        try:
            # Step 1: Resolve internal train_id
            info_url = "https://erail.in/rail/getTrains.aspx"
            info_resp = self.session.get(info_url, params={"TrainNo": train_no, "DataSource": "2"}, headers=self.HEADERS)
            trains = self._parse_train_list(info_resp.text)
            if not trains or not trains[0].get("train_id"): return None
            
            # Step 2: Fetch route data
            route_url = f"https://erail.in/data.aspx?Action=TRAINROUTE&Password=2012&Data1={trains[0]['train_id']}&Data2=0"
            route_resp = self.session.get(route_url, headers=self.HEADERS)
            return {
                "trainName": trains[0]["train_name"],
                "stations": self._parse_route_data(route_resp.text),
                "currentLocationInfo": "Schedule Data (erail.in) - Live delays not available"
            }
        except: return None

    def _parse_train_list(self, text):
        results = []
        for block in text.split("^"):
            parts = [p.strip() for p in block.split("~")]
            if len(parts) >= 2 and parts[0].isdigit():
                # Extract train_id (typically index 26)
                tid = ""
                for p in parts[25:35]: 
                    if p.isdigit() and p != parts[0]: tid = p; break
                results.append({"train_no": parts[0], "train_name": parts[1], "train_id": tid})
        return results

    def _parse_route_data(self, text):
        stations = []
        # Station data follows the '^' delimiter
        clean_text = text[text.find("^"):] if "^" in text else text
        for block in clean_text.split("^"):
            if not block.strip(): continue
            parts = [p.strip() for p in block.split("~")]
            if len(parts) < 8: continue
            
            # Find distance (index 15, 6, or 16 fallback)
            dist = 0
            for i in [15, 6, 16]:
                if i < len(parts) and parts[i].isdigit(): dist = int(parts[i]); break

            stations.append({
                "stationName": parts[2],
                "arrival": parts[3],
                "departure": parts[4],
                "distance": dist,
                "arrivalDelay": 0
            })
        return stations

class TrainVisualizer:
    """Encapsulates data visualization logic using Plotly."""
    
    @staticmethod
    def plot(status_data):
        d = status_data["data"]
        df = pd.DataFrame(d["stations"])
        
        fig = go.Figure()
        
        # Trace 1: Delays (Bar)
        fig.add_trace(go.Bar(
            x=df["stationName"], y=df["arrivalDelay"],
            name="Delay (min)", marker_color="indianred"
        ))
        
        # Trace 2: Progress (Line)
        fig.add_trace(go.Scatter(
            x=df["stationName"], y=df["distance"],
            name="Distance (km)", yaxis="y2", mode="lines+markers"
        ))

        fig.update_layout(
            title=f"<b>{d['trainName']}</b> - Status<br><sup>{d.get('currentLocationInfo', '')}</sup>",
            xaxis_title="Stations",
            yaxis=dict(title="Delay (min)", rangemode="tozero"),
            yaxis2=dict(title="Distance (km)", overlaying="y", side="right"),
            template="plotly_white",
            hovermode="x unified"
        )
        fig.show()

def main():
    print("="*40 + "\n  INDIAN RAILWAYS STATUS TOOL\n" + "="*40)
    
    key = os.getenv("IRCTC_RAPIDAPI_KEY")
    client = IndianRailwaysClient(rapidapi_key=key)
    
    query = input("Enter Train # or Name: ").strip()
    if not query: return

    # Resolve Train Number
    if not query.isdigit():
        results = client.search_trains(query)
        if not results: print("No trains found."); return
        print("\nSelect a train:")
        for i, t in enumerate(results[:5]): print(f"{i+1}. {t['train_no']} - {t['train_name']}")
        choice = input("Select (1-5): ")
        idx = int(choice)-1 if choice.isdigit() and 1 <= int(choice) <= len(results) else 0
        train_no = results[idx]["train_no"]
    else: train_no = query

    # Fetch and Visualize
    status = client.get_live_status(train_no)
    if status:
        TrainVisualizer.plot(status)
    else:
        print("[!] Could not retrieve data for this train.")

if __name__ == "__main__":
    main()
