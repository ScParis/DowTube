import customtkinter as ctk
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from gui import DownloaderGUI
from error_reporter import setup_error_handling

def main():
    try:
        # Set appearance mode and default color theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Configurar error reporting
        setup_error_handling(
            token=os.environ.get('GITHUB_TOKEN'),
            repo_owner=os.environ.get('GITHUB_REPO_OWNER'),
            repo_name=os.environ.get('GITHUB_REPO_NAME')
        )
        
        # Create the main window
        app = DownloaderGUI()
        
        # Start the application
        app.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
