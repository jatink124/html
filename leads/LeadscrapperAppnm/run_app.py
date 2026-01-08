import streamlit.web.cli as stcli
import os, sys

def resolve_path(path):
    """Helper to find the file path when inside the .exe"""
    if getattr(sys, "frozen", False):
        # If running as an .exe, look in the temporary folder
        basedir = sys._MEIPASS
    else:
        # If running as a script, look in the current folder
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    # Point to your main app file
    app_path = resolve_path("app.py")
    
    # Fake the command line arguments to start Streamlit
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    
    # Start the app
    sys.exit(stcli.main())