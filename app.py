from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"residents": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_resident_id():
    data = load_data()
    return f"PAP{len(data['residents']) + 1001}"

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', residents=data['residents'])

@app.route('/add_person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        data = load_data()
        
        # Handle file upload
        photo_url = ''
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                photo_url = f"uploads/{filename}"
        
        new_resident = {
            "id": generate_resident_id(),
            "name": request.form['name'],
            "age": int(request.form['age']),
            "gender": request.form['gender'],
            "address": request.form['address'],
            "contact": request.form['contact'],
            "email": request.form.get('email', ''),
            "blood_group": request.form.get('blood_group', ''),
            "photo_url": photo_url,
            "disease_stats": {
                "corona": f"{request.form.get('disease_corona', 0)}%",
                "dengue": f"{request.form.get('disease_dengue', 0)}%",
                "malaria": f"{request.form.get('disease_malaria', 0)}%"
            }
        }
        
        data['residents'].append(new_resident)
        save_data(data)
        flash('Resident added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_person.html')

@app.route('/resident/<resident_id>')
def resident_profile(resident_id):
    data = load_data()
    resident = next((r for r in data['residents'] if r['id'] == resident_id), None)
    if resident:
        return render_template('profile.html', resident=resident)
    flash('Resident not found!', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<resident_id>', methods=['POST'])
def delete_resident(resident_id):
    try:
        data = load_data()
        initial_count = len(data['residents'])
        data['residents'] = [r for r in data['residents'] if r['id'] != resident_id]
        
        if len(data['residents']) < initial_count:
            save_data(data)
            flash('Resident deleted successfully!', 'success')
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Resident not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)