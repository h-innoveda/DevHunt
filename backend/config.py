import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Uploads directory
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

# File paths
DB_PATH = os.path.join(DATA_DIR, 'devhunt.db')
KEYS_PATH = os.path.join(DATA_DIR, 'keys.json')
PROFILE_PATH = os.path.join(DATA_DIR, 'profile.json')
SETTINGS_PATH = os.path.join(DATA_DIR, 'settings.json')
LEARNING_PATH_JSON = os.path.join(DATA_DIR, 'learning_path.json')

# Key Manager settings
COOLING_DOWN_PERIOD = 60  # seconds

# Encryption key (used to secure stored API keys locally)
ENCRYPTION_KEY_FILE = os.path.join(DATA_DIR, '.secret')
if not os.path.exists(ENCRYPTION_KEY_FILE):
    from cryptography.fernet import Fernet
    secret = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, 'wb') as f:
        f.write(secret)
else:
    with open(ENCRYPTION_KEY_FILE, 'rb') as f:
        secret = f.read()

ENCRYPTION_SECRET = secret
