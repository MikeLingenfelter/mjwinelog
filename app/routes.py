import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_
import pandas as pd
import io
from app.models import db, Wine

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/')
@login_required
def index():
    return redirect(url_for('main.wines'))

@main.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

@main.route('/wines')
@login_required
def wines():
    # Get filter parameters
    search = request.args.get('search', '')
    varietal = request.args.get('varietal', '')
    origin = request.args.get('origin', '')
    rating_min = request.args.get('rating_min', '')
    rating_max = request.args.get('rating_max', '')
    favorites_only = request.args.get('favorites', '') == 'true'
    sort_by = request.args.get('sort', 'date_had')
    sort_order = request.args.get('order', 'desc')
    
    # Build query
    query = Wine.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Wine.vineyard.ilike(f'%{search}%'),
                Wine.varietal.ilike(f'%{search}%'),
                Wine.notes.ilike(f'%{search}%')
            )
        )
    
    if varietal:
        query = query.filter(Wine.varietal.ilike(f'%{varietal}%'))
    
    if origin:
        query = query.filter(Wine.origin.ilike(f'%{origin}%'))
    
    if rating_min:
        query = query.filter(Wine.rating >= float(rating_min))
    
    if rating_max:
        query = query.filter(Wine.rating <= float(rating_max))
    
    if favorites_only:
        query = query.filter(Wine.is_favorite == True)
    
    # Apply sorting
    if hasattr(Wine, sort_by):
        column = getattr(Wine, sort_by)
        if sort_order == 'desc':
            query = query.order_by(column.desc().nullslast())
        else:
            query = query.order_by(column.asc().nullslast())
    
    wines_list = query.all()
    
    # Get unique values for filter dropdowns
    all_varietals = db.session.query(Wine.varietal).filter_by(user_id=current_user.id).distinct().all()
    all_origins = db.session.query(Wine.origin).filter_by(user_id=current_user.id).distinct().all()
    
    varietals = sorted([v[0] for v in all_varietals if v[0]])
    origins = sorted([o[0] for o in all_origins if o[0]])
    
    return render_template('wines.html', 
                         wines=wines_list,
                         varietals=varietals,
                         origins=origins,
                         current_filters={
                             'search': search,
                             'varietal': varietal,
                             'origin': origin,
                             'rating_min': rating_min,
                             'rating_max': rating_max,
                             'favorites': favorites_only,
                             'sort': sort_by,
                             'order': sort_order
                         })

@main.route('/wine/add', methods=['GET', 'POST'])
@login_required
def add_wine():
    if request.method == 'POST':
        wine = Wine(user_id=current_user.id)
        
        wine.vineyard = request.form.get('vineyard')
        wine.varietal = request.form.get('varietal')
        wine.vintage = int(request.form.get('vintage')) if request.form.get('vintage') else None
        
        date_str = request.form.get('date_had')
        wine.date_had = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        
        wine.origin = request.form.get('origin')
        wine.rating = float(request.form.get('rating')) if request.form.get('rating') else None
        wine.purchase_location = request.form.get('purchase_location')
        wine.wine_club_month = request.form.get('wine_club_month')
        wine.price = float(request.form.get('price')) if request.form.get('price') else None
        wine.notes = request.form.get('notes')
        wine.is_favorite = request.form.get('is_favorite') == 'on'
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                wine.photo_filename = filename
        
        db.session.add(wine)
        db.session.commit()
        
        flash('Wine added successfully!', 'success')
        return redirect(url_for('main.wines'))
    
    return render_template('add_wine.html')

@main.route('/wine/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_wine(id):
    wine = Wine.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        wine.vineyard = request.form.get('vineyard')
        wine.varietal = request.form.get('varietal')
        wine.vintage = int(request.form.get('vintage')) if request.form.get('vintage') else None
        
        date_str = request.form.get('date_had')
        wine.date_had = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        
        wine.origin = request.form.get('origin')
        wine.rating = float(request.form.get('rating')) if request.form.get('rating') else None
        wine.purchase_location = request.form.get('purchase_location')
        wine.wine_club_month = request.form.get('wine_club_month')
        wine.price = float(request.form.get('price')) if request.form.get('price') else None
        wine.notes = request.form.get('notes')
        wine.is_favorite = request.form.get('is_favorite') == 'on'
        
        # Handle file upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                # Delete old photo if exists
                if wine.photo_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], wine.photo_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                wine.photo_filename = filename
        
        db.session.commit()
        flash('Wine updated successfully!', 'success')
        return redirect(url_for('main.wines'))
    
    return render_template('edit_wine.html', wine=wine)

@main.route('/wine/delete/<int:id>', methods=['POST'])
@login_required
def delete_wine(id):
    wine = Wine.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Delete photo if exists
    if wine.photo_filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], wine.photo_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(wine)
    db.session.commit()
    
    flash('Wine deleted successfully!', 'success')
    return redirect(url_for('main.wines'))

@main.route('/wine/toggle_favorite/<int:id>', methods=['POST'])
@login_required
def toggle_favorite(id):
    wine = Wine.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    wine.is_favorite = not wine.is_favorite
    db.session.commit()
    return jsonify({'success': True, 'is_favorite': wine.is_favorite})

@main.route('/statistics')
@login_required
def statistics():
    wines = Wine.query.filter_by(user_id=current_user.id).all()
    
    if not wines:
        return render_template('statistics.html', stats={})
    
    # Calculate statistics
    ratings_by_varietal = {}
    count_by_varietal = {}
    total_spent = 0
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    wines_by_month = {}
    
    for wine in wines:
        # Ratings by varietal
        if wine.varietal:
            if wine.varietal not in ratings_by_varietal:
                ratings_by_varietal[wine.varietal] = []
            if wine.rating:
                ratings_by_varietal[wine.varietal].append(wine.rating)
            
            count_by_varietal[wine.varietal] = count_by_varietal.get(wine.varietal, 0) + 1
        
        # Total spent
        if wine.price:
            total_spent += wine.price
        
        # Rating distribution
        if wine.rating:
            rating_bucket = int(wine.rating)
            rating_distribution[rating_bucket] = rating_distribution.get(rating_bucket, 0) + 1
        
        # Wines by month
        if wine.date_had:
            month_key = wine.date_had.strftime('%Y-%m')
            wines_by_month[month_key] = wines_by_month.get(month_key, 0) + 1
    
    # Average ratings by varietal
    avg_ratings_by_varietal = {
        varietal: sum(ratings) / len(ratings)
        for varietal, ratings in ratings_by_varietal.items()
    }
    
    # Sort by average rating
    top_varietals = sorted(avg_ratings_by_varietal.items(), key=lambda x: x[1], reverse=True)[:10]
    
    stats = {
        'total_wines': len(wines),
        'total_spent': total_spent,
        'avg_rating': sum(w.rating for w in wines if w.rating) / len([w for w in wines if w.rating]) if any(w.rating for w in wines) else 0,
        'top_varietals': top_varietals,
        'count_by_varietal': sorted(count_by_varietal.items(), key=lambda x: x[1], reverse=True)[:10],
        'rating_distribution': rating_distribution,
        'wines_by_month': sorted(wines_by_month.items()),
        'favorites_count': len([w for w in wines if w.is_favorite])
    }
    
    return render_template('statistics.html', stats=stats)

@main.route('/export')
@login_required
def export_wines():
    wines = Wine.query.filter_by(user_id=current_user.id).all()
    
    data = []
    for wine in wines:
        data.append({
            'Vineyard': wine.vineyard,
            'Varietal': wine.varietal,
            'Vintage': wine.vintage,
            'Date Had': wine.date_had.isoformat() if wine.date_had else '',
            'Origin': wine.origin,
            'Rating': wine.rating,
            'Purchase Location': wine.purchase_location,
            'Wine Club Month': wine.wine_club_month,
            'Price': wine.price,
            'Notes': wine.notes,
            'Is Favorite': wine.is_favorite
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'wine_collection_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@main.route('/import', methods=['GET', 'POST'])
@login_required
def import_wines():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file)
                
                imported_count = 0
                for _, row in df.iterrows():
                    wine = Wine(user_id=current_user.id)
                    
                    wine.vineyard = row.get('Vineyard')
                    wine.varietal = row.get('Varietal')
                    wine.vintage = int(row.get('Vintage')) if pd.notna(row.get('Vintage')) else None
                    
                    date_str = row.get('Date Had')
                    if pd.notna(date_str):
                        try:
                            wine.date_had = pd.to_datetime(date_str).date()
                        except:
                            pass
                    
                    wine.origin = row.get('Origin')
                    wine.rating = float(row.get('Rating')) if pd.notna(row.get('Rating')) else None
                    wine.purchase_location = row.get('Purchase Location')
                    wine.wine_club_month = row.get('Wine Club Month')
                    wine.price = float(row.get('Price')) if pd.notna(row.get('Price')) else None
                    wine.notes = row.get('Notes')
                    wine.is_favorite = row.get('Is Favorite', False) in [True, 'True', 'true', 1, '1']
                    
                    db.session.add(wine)
                    imported_count += 1
                
                db.session.commit()
                flash(f'Successfully imported {imported_count} wines!', 'success')
                return redirect(url_for('main.wines'))
            
            except Exception as e:
                flash(f'Error importing CSV: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('import.html')
