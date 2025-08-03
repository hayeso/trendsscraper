"""Entry point to start the Trends Compare app."""
import threading
import time
import webbrowser

import uvicorn
from backend.main import app


def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
