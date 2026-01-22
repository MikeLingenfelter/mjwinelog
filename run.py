from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=False)
