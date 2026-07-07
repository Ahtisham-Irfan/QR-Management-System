from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, QRCode, Category, ActivityLog
from utils import generate_qr_code, format_qr_content
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import csv
import io

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qr_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Reads from .env if present, otherwise falls back to a dev default.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

QR_CODE_DIR = os.path.join(app.static_folder, 'qr_codes')
os.makedirs(QR_CODE_DIR, exist_ok=True)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400

        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return jsonify({'error': 'Invalid credentials'}), 401
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    qrs = QRCode.query.filter_by(user_id=current_user.id).order_by(QRCode.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('dashboard.html', qrs=qrs, categories=categories)


@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        qr_type = data.get('qr_type')
        title = data.get('title')
        fill_color = data.get('fill_color', '#000000')
        back_color = data.get('back_color', '#FFFFFF')

        if not qr_type or not title:
            return jsonify({'error': 'Title and QR type are required'}), 400

        # Format content based on QR type
        content_data = data.get('content', {})
        formatted_content = format_qr_content(qr_type, content_data)

        if not formatted_content:
            return jsonify({'error': 'Content is required for this QR type'}), 400

        # Generate QR code (returns just the filename, e.g. "abc123.png")
        filename = generate_qr_code(formatted_content, fill_color, back_color)

        # Store only the filename in the DB — the "static/qr_codes/" part
        # is a rendering detail, not data, so we compute it wherever we need it.
        qr = QRCode(
            title=title,
            qr_type=qr_type,
            content=formatted_content,
            file_path=filename,
            user_id=current_user.id,
            fill_color=fill_color,
            back_color=back_color
        )
        db.session.add(qr)

        log = ActivityLog(action='Generated QR Code', user_id=current_user.id, details=f'Title: {title}')
        db.session.add(log)
        db.session.commit()

        image_url = url_for('static', filename=f'qr_codes/{filename}')
        return jsonify({'success': True, 'qr_id': qr.id, 'file_path': image_url})

    return render_template('generate.html')


@app.route('/download/<int:qr_id>')
@login_required
def download(qr_id):
    qr = QRCode.query.get(qr_id)
    if not qr or qr.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    qr.downloads += 1
    log = ActivityLog(action='Downloaded QR Code', user_id=current_user.id, details=f'QR ID: {qr_id}')
    db.session.add(log)
    db.session.commit()

    safe_title = "".join(c for c in qr.title if c.isalnum() or c in (' ', '-', '_')).strip() or 'qr_code'
    return send_from_directory(QR_CODE_DIR, qr.file_path, as_attachment=True,
                                download_name=f'{safe_title}.png')


@app.route('/delete/<int:qr_id>', methods=['DELETE'])
@login_required
def delete(qr_id):
    qr = QRCode.query.get(qr_id)
    if not qr or qr.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    full_path = os.path.join(QR_CODE_DIR, qr.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)

    db.session.delete(qr)
    db.session.commit()

    return jsonify({'success': True})


@app.route('/bulk-upload', methods=['POST'])
@login_required
def bulk_upload():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        csv_reader = csv.DictReader(stream)

        count = 0
        for row in csv_reader:
            title = row.get('title')
            qr_type = row.get('type', 'URL')
            content_data = {'content': row.get('content')}

            formatted_content = format_qr_content(qr_type, content_data)
            filename = generate_qr_code(formatted_content)

            qr = QRCode(
                title=title,
                qr_type=qr_type,
                content=formatted_content,
                file_path=filename,
                user_id=current_user.id
            )
            db.session.add(qr)
            count += 1

        db.session.commit()
        return jsonify({'success': True, 'message': f'Bulk upload completed ({count} QR codes created)'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/history')
@login_required
def history():
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).all()
    return render_template('history.html', logs=logs)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
