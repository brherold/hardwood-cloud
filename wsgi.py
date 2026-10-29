import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
for p in [ROOT_DIR, FRONTEND_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from frontend.webapp import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
