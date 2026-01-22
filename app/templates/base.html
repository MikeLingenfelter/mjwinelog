import os
import shutil
from datetime import datetime

def backup_database(app):
    """Create a backup of the SQLite database"""
    with app.app_context():
        try:
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            backup_folder = os.environ.get('BACKUP_FOLDER', 'backups')
            
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'wines_backup_{timestamp}.db'
            backup_path = os.path.join(backup_folder, backup_filename)
            
            shutil.copy2(db_path, backup_path)
            
            # Keep only last 30 backups
            backups = sorted([f for f in os.listdir(backup_folder) if f.startswith('wines_backup_')])
            if len(backups) > 30:
                for old_backup in backups[:-30]:
                    os.remove(os.path.join(backup_folder, old_backup))
            
            print(f'Database backup created: {backup_filename}')
            return True
        except Exception as e:
            print(f'Backup failed: {str(e)}')
            return False
