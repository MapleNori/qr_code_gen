import tkinter as tk
from tkinter import ttk, Canvas
from person2_speedtest import SpeedTest
from person3_graph import SpeedResults, ThemeManager
import threading
import math
import itertools

def show_loading(canvas, stop_event):
    """Displays a rotating loading animation while speed test is in progress."""
    canvas.delete("all")
    
    # Enhanced loading animation with more dots and smoother transition
    positions = [(100, 40), (120, 50), (140, 60), (150, 80), (160, 100), (150, 120), 
                (140, 140), (120, 150), (100, 160), (80, 150), (60, 140), (50, 120), 
                (40, 100), (50, 80), (60, 60), (80, 50)]
    colors = itertools.cycle(["#00ff00", "#ffffff"])  # Green & White Glow

    def animate(index=0):
        if stop_event.is_set():  # Stop animation when test completes
            return
        
        canvas.delete("all")
        for i in range(len(positions)):
            # Create glowing effect with fade based on distance from active dot
            distance = (i - index) % len(positions)
            if distance == 0:
                color = next(colors)
                size = 6  # Larger active dot
            else:
                # Calculate a fading effect
                fade = max(0, 1 - (distance / (len(positions) / 2)))
                # Convert fade to hex intensity
                intensity = int(fade * 255)
                color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                size = 4  # Smaller inactive dots
                
            x, y = positions[i]
            canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline=color)
            
        index = (index + 1) % len(positions)
        canvas.after(80, animate, index)  # Slightly faster animation

    animate()

class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test")
        self.root.geometry("500x600")  # Slightly larger window for better spacing
        
        # Enable responsive window sizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.theme_manager = ThemeManager("Tech Neon")  # Default theme
        self.speed_tester = SpeedTest()
        self.results = SpeedResults()
        self.loading_stop = threading.Event()  # Event to stop loading animation

        # Main container frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # App title with improved styling
        self.title_frame = tk.Frame(self.main_frame)
        self.title_frame.pack(fill=tk.X, pady=10)
        
        self.label = tk.Label(self.title_frame, text="INTERNET SPEED TEST", font=("Arial", 18, "bold"))
        self.label.pack(pady=10)
        
        # Separator for visual division
        ttk.Separator(self.main_frame).pack(fill=tk.X, pady=5)

        # Canvas for speed meter and loading animation
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(pady=10)
        self.canvas = Canvas(self.canvas_frame, width=200, height=200, highlightthickness=0)
        self.canvas.pack()

        # Info panel with better organization
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.speed_label = tk.Label(self.info_frame, text="Speed: -- Mbps", font=("Arial", 14))
        self.speed_label.pack(pady=5)
        
        self.isp_label = tk.Label(self.info_frame, text="ISP: Detecting...", font=("Arial", 12))
        self.isp_label.pack(pady=5)
        
        # Styling for all labels
        self.speed_label.config(relief=tk.GROOVE, padx=10, pady=5)
        self.isp_label.config(relief=tk.GROOVE, padx=10, pady=5)

        # Button frame with improved styling and organization
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=15)
        
        # Create a custom style for the buttons
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 11), padding=8)
        
        self.test_button = ttk.Button(
            self.button_frame, 
            text="▶ Start Speed Test", 
            command=self.run_test,
            style="TButton"
        )
        self.test_button.pack(pady=10, padx=20, fill=tk.X)
        
        self.results_button = ttk.Button(
            self.button_frame, 
            text="📊 View Previous Results", 
            command=self.view_results,
            style="TButton"
        )
        self.results_button.pack(pady=5, padx=20, fill=tk.X)
        
        self.theme_switch = ttk.Button(
            self.button_frame, 
            text="🎨 Switch Theme", 
            command=self.switch_theme,
            style="TButton"
        )
        self.theme_switch.pack(pady=5, padx=20, fill=tk.X)

        # Status bar at the bottom
        self.status_frame = tk.Frame(self.main_frame, relief=tk.SUNKEN, bd=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.status_label = tk.Label(self.status_frame, text="Ready to test", font=("Arial", 9), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Apply themes to all elements
        self.update_theme()
        
        # Initial drawing of speed meter
        self.draw_speed_meter()

    def update_theme(self):
        """Apply current theme to all widgets"""
        self.theme_manager.apply_theme(self.root, "bg")
        self.theme_manager.apply_theme(self.main_frame, "bg")
        self.theme_manager.apply_theme(self.title_frame, "bg")
        self.theme_manager.apply_theme(self.canvas_frame, "bg")
        self.theme_manager.apply_theme(self.info_frame, "bg")
        self.theme_manager.apply_theme(self.button_frame, "bg")
        self.theme_manager.apply_theme(self.status_frame, "bg")
        self.theme_manager.apply_theme(self.label, "text")
        self.theme_manager.apply_theme(self.speed_label, "text")
        self.theme_manager.apply_theme(self.isp_label, "text")
        self.theme_manager.apply_theme(self.status_label, "text")

    def run_test(self):
        """Starts the speed test and shows loading animation."""
        self.test_button["state"] = "disabled"
        self.status_label.config(text="Running speed test...")
        self.speed_label.config(text="Testing in progress...")
        self.loading_stop.clear()  # Reset stop event
        show_loading(self.canvas, self.loading_stop)  # Start loading animation
        threading.Thread(target=self.perform_test, daemon=True).start()

    def perform_test(self):
        """Runs the speed test and updates the UI."""
        ping = self.speed_tester.get_ping()
        download_speed = self.speed_tester.get_download_speed()
        upload_speed = self.speed_tester.get_upload_speed()
        isp = self.speed_tester.get_real_isp()  # Fetch real ISP

        self.results.store_result(ping, download_speed, upload_speed)
        self.isp_label.config(text=f"ISP: {isp}")

        self.loading_stop.set()  # Stop loading animation
        self.canvas.delete("all")  # Clear loading
        self.animate_meter(download_speed)  # Show speed meter

        # Format the results with improved readability
        if isinstance(download_speed, (int, float)) and isinstance(upload_speed, (int, float)) and isinstance(ping, (int, float)):
            self.speed_label.config(text=(
                f"Download: {download_speed:.2f} Mbps\n"
                f"Upload: {upload_speed:.2f} Mbps\n"
                f"Ping: {ping:.1f} ms"
            ))
            self.status_label.config(text=f"Test completed. Download: {download_speed:.2f} Mbps")
        else:
            self.speed_label.config(text=(
                f"Download: {download_speed} Mbps\n"
                f"Upload: {upload_speed} Mbps\n"
                f"Ping: {ping} ms"
            ))
            self.status_label.config(text="Test completed with errors")

        self.test_button["state"] = "normal"  # Re-enable button

    def draw_speed_meter(self):
        """Draws the speed meter with enhanced visual design."""
        self.canvas.delete("all")
        
        # Draw background circle
        self.canvas.create_oval(10, 10, 190, 190, outline="#333333", width=2, fill="#f0f0f0")
        
        # Draw arc segments for speed ranges
        self.draw_colored_arcs()
        
        # Draw center circle
        self.canvas.create_oval(90, 90, 110, 110, fill="black", outline="black")
        
        # Draw speed labels with improved readability
        for i in range(0, 181, 30):
            angle = math.radians(i - 90)
            r_outer = 85  # Radius for the text
            r_inner = 75  # Radius for the tick marks
            
            # Position for text
            x_text = 100 + r_outer * math.cos(angle)
            y_text = 100 + r_outer * math.sin(angle)
            
            # Position for tick marks
            x1 = 100 + r_inner * math.cos(angle)
            y1 = 100 + r_inner * math.sin(angle)
            x2 = 100 + (r_inner - 8) * math.cos(angle)
            y2 = 100 + (r_inner - 8) * math.sin(angle)
            
            # Draw tick mark
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="black")
            
            # Draw text
            self.canvas.create_text(x_text, y_text, text=str(i // 10 * 10), 
                                    font=("Arial", 10, "bold"), fill="black")

        # Create speed label at the bottom
        self.canvas.create_text(100, 155, text="Mbps", font=("Arial", 12, "bold"), fill="black")
        
        # Draw initial needle
        self.needle = self.canvas.create_line(100, 100, 100, 30, width=3, fill="red", arrow=tk.LAST)

    def draw_colored_arcs(self):
        """Draws colored arcs for different speed ranges."""
        # Slow speeds (0-30 Mbps) - Red to Yellow
        for i in range(0, 30):
            angle1 = -90 + (i * 180 / 100)
            angle2 = -90 + ((i + 1) * 180 / 100)
            # Gradient from red to yellow
            r = min(255, int(255 * (i / 30)))
            g = min(255, int(255 * (i / 30)))
            color = f"#{r:02x}{g:02x}00"
            self.draw_arc_segment(angle1, angle2, color)
            
        # Medium speeds (30-70 Mbps) - Yellow to Green
        for i in range(30, 70):
            angle1 = -90 + (i * 180 / 100)
            angle2 = -90 + ((i + 1) * 180 / 100)
            # Gradient from yellow to green
            g = 255
            r = max(0, int(255 * (1 - (i - 30) / 40)))
            color = f"#{r:02x}{g:02x}00"
            self.draw_arc_segment(angle1, angle2, color)
            
        # Fast speeds (70-100 Mbps) - Green
        for i in range(70, 100):
            angle1 = -90 + (i * 180 / 100)
            angle2 = -90 + ((i + 1) * 180 / 100)
            self.draw_arc_segment(angle1, angle2, "#00ff00")  # Bright green

    def draw_arc_segment(self, angle1, angle2, color):
        """Helper to draw a colored arc segment on the meter."""
        # Convert angles from degrees to tkinter's arc format
        start = angle1 + 90
        extent = angle2 - angle1
        
        # Draw arc (tkinter angles: 0=east, 90=south, etc.)
        self.canvas.create_arc(20, 20, 180, 180, 
                              start=start, extent=extent,
                              outline="", width=0, fill=color, style=tk.PIESLICE)
        
        # Overlay with a smaller white circle to create the gauge effect
        self.canvas.create_oval(35, 35, 165, 165, fill="#f0f0f0", outline="")

    def animate_meter(self, speed):
        """Animates the speed meter needle based on the test results with smooth transition."""
        self.draw_speed_meter()

        if not isinstance(speed, (int, float)):
            # Handle error case
            speed = 0
        
        # Cap at 100 Mbps
        speed = min(float(speed), 100)
        
        # Create smooth animation
        current_angle = -90  # Start at minimum position
        target_angle = -90 + (speed / 100) * 180
        
        def animate_step(current):
            if abs(current - target_angle) < 1:
                # Final position
                angle = math.radians(target_angle - 90)
                x = 100 + 80 * math.cos(angle)
                y = 100 + 80 * math.sin(angle)
                self.canvas.coords(self.needle, 100, 100, x, y)
                
                # Display the speed value in center of gauge
                self.canvas.create_text(100, 125, text=f"{speed:.1f}", 
                                       font=("Arial", 16, "bold"), fill="black")
                return
                
            # Calculate new position
            new_angle = current + (target_angle - current) * 0.2
            angle = math.radians(new_angle - 90)
            x = 100 + 80 * math.cos(angle)
            y = 100 + 80 * math.sin(angle)
            self.canvas.coords(self.needle, 100, 100, x, y)
            
            # Continue animation
            self.canvas.after(20, animate_step, new_angle)
            
        animate_step(current_angle)

    def view_results(self):
        """Displays previous test results as a graph."""
        if not self.results.results:
            self.status_label.config(text="No previous results to display.")
            return
            
        self.status_label.config(text="Displaying results graph...")
        self.results.plot_results()

    def switch_theme(self):
        """Switches between Tech Neon and Soft Blue themes."""
        new_theme = "Soft Blue" if self.theme_manager.theme == self.theme_manager.THEMES["Tech Neon"] else "Tech Neon"
        self.theme_manager = ThemeManager(new_theme)
        
        # Update all widget themes
        self.update_theme()
        
        # Redraw the speed meter with new theme colors
        self.draw_speed_meter()
        
        theme_name = "Tech Neon" if new_theme == "Tech Neon" else "Soft Blue"
        self.status_label.config(text=f"Theme changed to {theme_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()
