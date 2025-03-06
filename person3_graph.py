import matplotlib.pyplot as plt
from datetime import datetime

class SpeedResults:
    def __init__(self):
        self.results = []

    def store_result(self, ping, download, upload):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results.append((timestamp, ping, download, upload))

    def plot_results(self):
        if not self.results:
            print("No previous results to display.")
            return

        timestamps, pings, downloads, uploads = zip(*self.results)

        plt.figure(figsize=(8, 4))
        plt.plot(timestamps, downloads, label="Download Speed (Mbps)", marker="o", color="blue")
        plt.plot(timestamps, uploads, label="Upload Speed (Mbps)", marker="s", color="green")
        plt.xlabel("Time")
        plt.ylabel("Speed (Mbps)")
        plt.title("Internet Speed Test Results")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

class ThemeManager:
    THEMES = {
        "Tech Neon": {"bg": "black", "text": "black", "button_bg": "#00ff00", "button_fg": "black"},
        "Soft Blue": {"bg": "lightblue", "text": "black", "button_bg": "white", "button_fg": "black"}
    }

    def __init__(self, theme_name):
        self.theme = self.THEMES.get(theme_name, self.THEMES["Tech Neon"])

    def apply_theme(self, widget, element):
        if element == "text":
            widget.config(fg=self.theme["text"])
        else:
            widget.config(bg=self.theme["bg"])