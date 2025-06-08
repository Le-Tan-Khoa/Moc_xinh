import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ADMIN_EMAIL = 'admin@mocxinh.vn'
ADMIN_PASS = '123456'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cấu hình database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)

# Model sản phẩm
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    stone = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    img = db.Column(db.String(200), nullable=False)

# Tạo bảng nếu chưa có
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = 6
    total = Product.query.count()
    products = Product.query.order_by(Product.id.desc()).offset((page-1)*per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page
    return render_template(
        'index.html',
        products=products,
        page=page,
        total_pages=total_pages
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Sai email hoặc mật khẩu!', 'danger')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        stone = request.form['stone']
        size = request.form['size']
        file = request.files['img']
        img_url = ""
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = url_for('static', filename=f'uploads/{filename}')
        new_product = Product(name=name, stone=stone, size=size, img=img_url)
        db.session.add(new_product)
        db.session.commit()
        flash('Đã thêm sản phẩm mới!', 'success')
        return redirect(url_for('admin_dashboard'))
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin_dashboard.html', products=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))