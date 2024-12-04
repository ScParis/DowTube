import customtkinter as ctk
from src.gui import DownloaderGUI

def main():
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Create the main window
    app = DownloaderGUI()
    
    # Start the application
    app.mainloop()

if __name__ == "__main__":
    main()
