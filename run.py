from app import create_app
import os

# Create the app instance at module level
app = create_app()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    # Run the application
    # IMPORTANT: host='0.0.0.0' allows external connections to the container
    # Use threaded=True to allow APScheduler to work properly
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)