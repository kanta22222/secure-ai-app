Secure AI File Desktop App (Python)

Quick start (PowerShell)
# create and activate venv
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

# install
pip install -r requirements.txt

# run the app
python app\\\main.py

Run tests
pytest -q

Notes
- The app stores the DB in `data/app.db` and encrypted files in `storage/`.
- For demo the encryption key is stored at `data/fernet.key`. In production use a secret manager.
- To make the UI more "breathtaking", swap Qt stylesheets, add icons and animations.
