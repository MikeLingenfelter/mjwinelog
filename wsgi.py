"""
WSGI entry point for production deployment
"""
import os
from app import create_app

# Ensure upload directory exists
os.makedirs('/app/uploads', exist_ok=True)

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # This allows running with: python wsgi.py
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)