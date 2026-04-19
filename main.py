from flask import request, redirect, Flask, render_template
from forms.forms import *
from data.users import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import data.db_session as db_session

from data.products import Product
from data.product_images import ProductImage
import os
from datetime import datetime


db_session.global_init('db/shop.db')

app = Flask(__name__)
app.secret_key = 'dev_secret_key_123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    session = db_session.create_session()
    products = session.query(Product).filter(Product.stock > 0).all()
    session.close()
    return render_template('index.html', products=products)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    session.close()
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        session = db_session.create_session()
        if session.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', form=form, error='Username exists')
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, error='Email exists')

        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        user.role = 'user'
        session.add(user)
        session.commit()
        session.close()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        session = db_session.create_session()
        user = session.query(User).filter(
            User.username == form.username.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect('/')
        return render_template('login.html', form=form, error='Invalid credentials')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not current_user.is_seller() and not current_user.is_admin():
        return redirect('/')

    form = ProductForm(request.form)
    if request.method == 'POST' and form.validate():
        product = Product()
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.stock = form.stock.data
        product.seller_id = current_user.id

        session_db = db_session.create_session()
        session_db.add(product)
        session_db.commit()

        images = request.files.getlist('images')
        for i, image in enumerate(images):
            if image and image.filename:
                filename = secure_filename(
                    f"{datetime.now().timestamp()}_{i}_{image.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                product_image = ProductImage()
                product_image.product_id = product.id
                product_image.image_url = filename
                product_image.is_main = (i == 0)
                product_image.sort_order = i
                session_db.add(product_image)
        session_db.commit()
        session_db.close()
        return redirect('/')
    return render_template('add_product.html', form=form)


@app.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    session_db = db_session.create_session()
    product = session_db.query(Product).filter(
        Product.id == product_id).first()
    if not product:
        session_db.close()
        return redirect('/')

    if not current_user.is_admin() and not current_user.is_seller():
        session_db.close()
        return redirect('/')

    _ = product.images

    form = ProductForm(request.form)
    if request.method == 'POST' and form.validate():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.stock = form.stock.data

        images = request.files.getlist('images')
        for i, image in enumerate(images):
            if image and image.filename:
                filename = secure_filename(
                    f"{datetime.now().timestamp()}_{i}_{image.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                product_image = ProductImage()
                product_image.product_id = product.id
                product_image.image_url = filename
                product_image.is_main = (len(product.images) == 0 and i == 0)
                product_image.sort_order = len(product.images) + i
                session_db.add(product_image)
        session_db.commit()
        session_db.close()
        return redirect(f'/product/{product_id}')

    form.name.data = product.name
    form.description.data = product.description
    form.price.data = product.price
    form.category.data = product.category
    form.stock.data = product.stock
    session_db.close()
    return render_template('edit_product.html', form=form, product=product)


@app.route('/product/delete/<int:product_id>')
@login_required
def delete_product(product_id):
    if not current_user.is_admin() and not current_user.is_seller():
        return redirect('/')

    session_db = db_session.create_session()
    product = session_db.query(Product).filter(
        Product.id == product_id).first()
    if not product:
        session_db.close()
        return redirect('/')

    images = list(product.images)

    for image in images:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.image_url)
        if os.path.exists(filepath):
            os.remove(filepath)
    session_db.delete(product)
    session_db.commit()
    session_db.close()
    return redirect('/')


@app.route('/product/delete-image/<int:image_id>')
@login_required
def delete_product_image(image_id):
    if not current_user.is_admin() and not current_user.is_seller():
        return redirect('/')

    session_db = db_session.create_session()
    image = session_db.query(ProductImage).filter(
        ProductImage.id == image_id).first()
    if not image:
        session_db.close()
        return redirect('/')

    product_id = image.product_id
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.image_url)
    if os.path.exists(filepath):
        os.remove(filepath)

    session_db.delete(image)
    session_db.commit()
    session_db.close()
    return redirect(f'/product/edit/{product_id}')


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    session_db = db_session.create_session()
    product = session_db.query(Product).filter(
        Product.id == product_id).first()
    if not product:
        session_db.close()
        return redirect('/')

    _ = product.images
    _ = product.seller

    session_db.close()
    return render_template('product_detail.html', product=product)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
