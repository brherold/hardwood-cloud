import sys
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Alias so both 'extensions' and 'backend.extensions' resolve to this module instance
if 'backend.extensions' not in sys.modules:
    sys.modules['backend.extensions'] = sys.modules[__name__]
if 'extensions' not in sys.modules:
    sys.modules['extensions'] = sys.modules[__name__]