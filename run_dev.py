import os
import sys
import webbrowser
import threading
import time

# Ensure frontend and project root are in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
for p in [ROOT_DIR, FRONTEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from frontend.webapp import app

def open_browser(port):
    time.sleep(1.2)
    try:
        webbrowser.open(f"http://127.0.0.1:{port}/")
    except Exception:
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*58)
    print("🚀 Hardwood Local Dev Server Started!")
    print(f"👉 Local URL: http://127.0.0.1:{port}/")
    print("📝 Any edits to templates or Python code auto-reload live.")
    print("⏹️  Press Ctrl+C to stop.")
    print("="*58 + "\n")
    
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    app.run(host="127.0.0.1", port=port, debug=True)
