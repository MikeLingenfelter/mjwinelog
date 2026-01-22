#!/usr/bin/env python3
"""
Script to create an admin user for Wine Tracker
Run this inside the Docker container:
  docker exec -it wine-tracker python create_admin.py
"""

from app import create_app
from app.models import db, User
import getpass

def create_admin():
    app = create_app()
    
    with app.app_context():
        print("=== Create Admin User ===\n")
        
        username = input("Enter admin username: ").strip()
        
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"\nError: User '{username}' already exists!")
            return
        
        email = input("Enter admin email: ").strip()
        
        # Check if email exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"\nError: Email '{email}' is already in use!")
            return
        
        password = getpass.getpass("Enter admin password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("\nError: Passwords do not match!")
            return
        
        if len(password) < 6:
            print("\nError: Password must be at least 6 characters!")
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            role='admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"\n✓ Admin user '{username}' created successfully!")
        print(f"  Email: {email}")
        print(f"  Role: admin")
        print("\nYou can now login with these credentials.")

if __name__ == '__main__':
    create_admin()
