import webview
import threading
import sys
import os
from app import app

def start_server():
    app.run(port=5000, use_reloader=False)

if __name__ == '__main__':
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # Create a window
    abs_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(abs_path, 'static', 'images', 'logo.png')

    webview.create_window(
        title='Atomic Downloader', 
        url='http://127.0.0.1:5000',
        width=1000,
        height=800,
        resizable=True,
        icon=icon_path,
        background_color='#050505' # Match the CSS bg
    )
    
    # Start the GUI loop
    webview.start()
    sys.exit()
