import speedtest
import socket
import requests

class SpeedTest:
    def __init__(self):
        try:
            self.st = speedtest.Speedtest()
            self.st.get_best_server()
        except Exception as e:
            print("Error initializing Speedtest:", e)

    def get_ping(self):
        try:
            return round(self.st.results.ping, 2)
        except:
            return "Error"

    def get_download_speed(self):
        try:
            return round(self.st.download() / 1_000_000, 2)  # Convert to Mbps
        except:
            return "Error"

    def get_upload_speed(self):
        try:
            return round(self.st.upload() / 1_000_000, 2)  # Convert to Mbps
        except:
            return "Error"

    def get_real_isp(self):
        """Fetches real ISP information using ipinfo.io API."""
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            return data.get("org", "Unknown ISP")
        except:
            return "Unknown ISP"
