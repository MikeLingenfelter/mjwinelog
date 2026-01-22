# Wine Tracker

A self-hosted web application for tracking your wine collection with features for rating, searching, statistics, and more.

## Features

### Core Features
- ✅ Multi-user support with admin privileges
- ✅ Secure encrypted password storage
- ✅ User data isolation
- ✅ Track comprehensive wine details (vineyard, varietal, vintage, date, origin, rating, price, etc.)
- ✅ Sort and filter on all fields
- ✅ SQLite database (simple, file-based, easy to backup)
- ✅ CSV import/export

### Additional Features
- 🔍 Search across vineyard, varietal, and notes
- 📊 Statistics dashboard with visual charts
- 📸 Wine label photo uploads
- ⭐ Favorites/wishlist system
- 💾 Automated daily database backups
- 📱 Mobile-responsive design
- 🎯 Advanced multi-field filtering

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- A Linux server (tested on Ubuntu, works on most distributions)
- At least 1GB RAM and 5GB storage

### Installation

1. **Clone or create the project directory**
```bash
mkdir wine-tracker
cd wine-tracker
```

2. **Create the directory structure**
```bash
mkdir -p app/templates/admin data backups uploads
```

3. **Copy all the provided files into their respective locations:**
   - `docker-compose.yml` → root directory
   - `Dockerfile` → root directory
   - `requirements.txt` → root directory
   - `run.py` → root directory
   - `create_admin.py` → root directory
   - `.env.example` → root directory
   - `.gitignore` → root directory
   - All Python files → `app/` directory
   - All HTML files → `app/templates/` directory
   - Admin HTML files → `app/templates/admin/` directory

4. **Create environment file**
```bash
cp .env.example .env
```

5. **Generate a secure secret key**
```bash
# On Linux/Mac
python3 -c "import secrets; print(secrets.token_hex(32))"

# Or use openssl
openssl rand -hex 32
```

6. **Edit .env file with your secret key**
```bash
nano .env
# Update SECRET_KEY with the generated value
```

7. **Build and start the container**
```bash
docker-compose up -d --build
```

8. **Create your first admin user**
```bash
docker exec -it wine-tracker python create_admin.py
```

9. **Access the application**
```
http://your-server-ip:5000
```

## Deployment on Linode

### Option 1: Direct Deployment (Port 5000)

1. Create a Linode instance (Nanode 1GB is sufficient)
2. SSH into your server
3. Install Docker:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
```

4. Follow the installation steps above

5. Open port 5000 in your firewall:
```bash
sudo ufw allow 5000/tcp
sudo ufw enable
```

### Option 2: Production Deployment with Nginx + SSL (Recommended)

1. **Install Nginx**
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

2. **Create Nginx configuration** (`/etc/nginx/sites-available/wine-tracker`)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase upload size for wine photos
        client_max_body_size 20M;
    }
}
```

3. **Enable the site**
```bash
sudo ln -s /etc/nginx/sites-available/wine-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Get SSL certificate**
```bash
sudo certbot --nginx -d your-domain.com
```

5. **Access your site**
```
https://your-domain.com
```

## Usage

### Adding Wines
1. Click "Add Wine" in the navigation
2. Fill in the wine details
3. Optionally upload a photo of the wine label
4. Mark as favorite if desired
5. Click "Add Wine"

### Searching and Filtering
- Use the search box to find wines by vineyard, varietal, or notes
- Apply filters for varietal, origin, rating range
- Toggle "Favorites Only" to see your starred wines
- Click column headers to sort

### Statistics Dashboard
- View total wines, average rating, total spent
- See top-rated varietals
- Analyze rating distribution
- Track wines tasted by month

### Importing Wines
1. Prepare a CSV file with the required columns
2. Go to "Import" in the navigation
3. Upload your CSV file
4. All wines will be imported to your account

### Exporting Wines
- Click "Export" to download all your wines as CSV
- Use for backups or data analysis

### Admin Functions
- Admins can access the "Admin" menu
- Create new users
- Edit user details and roles
- Delete users (except yourself)

## Data Management

### Backups
- Automated daily backups run at 2:00 AM
- Backups are stored in `./backups/` directory
- Last 30 backups are retained automatically

### Manual Backup
```bash
# Copy the database file
docker exec wine-tracker cp /app/data/wines.db /app/backups/manual_backup_$(date +%Y%m%d).db

# Or copy to your local machine
docker cp wine-tracker:/app/data/wines.db ./wines_backup.db
```

### Restore from Backup
```bash
# Stop the container
docker-compose down

# Replace the database file
cp ./backups/wines_backup_YYYYMMDD_HHMMSS.db ./data/wines.db

# Start the container
docker-compose up -d
```

## Maintenance

### View Logs
```bash
docker-compose logs -f
```

### Restart Application
```bash
docker-compose restart
```

### Update Application
```bash
# Pull latest changes
git pull  # if using git

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Reset Everything (CAUTION: Deletes all data)
```bash
docker-compose down
sudo rm -rf data/ backups/ uploads/
docker-compose up -d --build
docker exec -it wine-tracker python create_admin.py
```

## Security Recommendations

1. **Use a strong SECRET_KEY** - Generate with `openssl rand -hex 32`
2. **Use HTTPS in production** - Set up with Let's Encrypt/Certbot
3. **Regular backups** - Set up automated backups to external storage
4. **Strong passwords** - Enforce minimum 8 characters for all users
5. **Firewall** - Only expose necessary ports (443 for HTTPS, 22 for SSH)
6. **Keep Docker updated** - Regularly update Docker and base images

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Ensure ports aren't in use
sudo netstat -tulpn | grep 5000

# Rebuild from scratch
docker-compose down
docker-compose up -d --build
```

### Can't create admin user
```bash
# Check if database exists
docker exec -it wine-tracker ls -la /app/data/

# Recreate database
docker exec -it wine-tracker python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### File upload not working
```bash
# Check permissions
docker exec -it wine-tracker ls -la /app/uploads/

# Fix permissions
docker exec -it wine-tracker chmod 777 /app/uploads/
```

### Port 5000 already in use
Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "8080:5000"  # Change 5000 to any available port
```

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Data Processing**: Pandas for CSV import/export
- **Image Processing**: Pillow for photo uploads
- **Task Scheduling**: APScheduler for automated backups
- **Containerization**: Docker

## File Structure

```
wine-tracker/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run.py
├── create_admin.py
├── .env
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── auth.py
│   ├── admin.py
│   ├── backup.py
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── wines.html
│       ├── add_wine.html
│       ├── edit_wine.html
│       ├── statistics.html
│       ├── import.html
│       └── admin/
│           ├── users.html
│           ├── add_user.html
│           └── edit_user.html
├── data/           # SQLite database (persistent)
├── backups/        # Automated backups (persistent)
└── uploads/        # Wine photos (persistent)
```

## License

This is a personal project created for self-hosting. Feel free to modify and use as needed.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Docker logs: `docker-compose logs`
3. Verify all files are in the correct locations
4. Ensure proper permissions on data directories

## Future Enhancement Ideas

- Email notifications for wine club deliveries
- Barcode/QR code scanning for wine lookup
- Integration with wine databases (Vivino, CellarTracker)
- Social features (share tasting notes with friends)
- Food pairing suggestions
- Wine aging predictions
- Cellar inventory management
- Price tracking and value appreciation

Enjoy tracking your wine journey! 🍷
