from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User
from data.products import Product
from data.product_images import ProductImage
from data.reviews import Review
from data.orders import Order
import os
from datetime import datetime
from forms.forms import *

app = Flask(__name__)
app.secret_key = 'secret_key_shop_12345_abcde'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    session_db = db_session.create_session()
    user = session_db.query(User).filter(User.id == user_id).first()
    session_db.close()
    return user


db_session.global_init('db/shop.db')


@app.context_processor
def utility_processor():
    return {
        'icons': {
            'logo': '/static/icons/logo.png',
            'home': '/static/icons/home.png',
            'products': '/static/icons/products.png',
            'add': '/static/icons/add.png',
            'orders': '/static/icons/orders.png',
            'user': '/static/icons/user.png',
            'logout': '/static/icons/logout.png',
            'login': '/static/icons/login.png',
            'register': '/static/icons/register.png',
            'edit': '/static/icons/edit.png',
            'delete': '/static/icons/delete.png',
        }
    }


@app.route('/')
def index():
    session_db = db_session.create_session()
    products = session_db.query(Product).filter(
        Product.stock > 0).order_by(Product.created_at.desc()).all()
    for product in products:
        _ = product.images
    session_db.close()
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        session_db = db_session.create_session()
        user = session_db.query(User).filter(
            User.username == form.username.data).first()
        session_db.close()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect('/')
        else:
            return render_template('login.html', form=form, error='Invalid username or password')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        session_db = db_session.create_session()

        if session_db.query(User).filter(User.username == form.username.data).first():
            session_db.close()
            return render_template('register.html', form=form, error='Username already exists')

        if session_db.query(User).filter(User.email == form.email.data).first():
            session_db.close()
            return render_template('register.html', form=form, error='Email already exists')

        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        user.role = 'user'
        session_db.add(user)
        session_db.commit()
        session_db.close()
        return redirect('/login')

    return render_template('register.html', form=form)


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

    reviews = session_db.query(Review).filter(
        Review.product_id == product_id).order_by(Review.created_at.desc()).all()
    for review in reviews:
        _ = review.user
    session_db.close()
    return render_template('product_detail.html', product=product, reviews=reviews)


@app.route('/review/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    form = ReviewForm(request.form)
    if form.validate():
        review = Review()
        review.product_id = product_id
        review.user_id = current_user.id
        review.rating = form.rating.data
        review.comment = form.comment.data
        session_db = db_session.create_session()
        session_db.add(review)
        session_db.commit()
        session_db.close()
    return redirect(f'/product/{product_id}')


@app.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    session_db = db_session.create_session()
    review = session_db.query(Review).filter(Review.id == review_id).first()
    if not review:
        session_db.close()
        return redirect('/')
    product_id = review.product_id
    if not current_user.is_admin() and review.user_id != current_user.id:
        session_db.close()
        return redirect(f'/product/{product_id}')

    form = ReviewForm(request.form)
    if request.method == 'POST' and form.validate():
        review.rating = form.rating.data
        review.comment = form.comment.data
        session_db.commit()
        session_db.close()
        return redirect(f'/product/{product_id}')

    form.rating.data = review.rating
    form.comment.data = review.comment
    session_db.close()
    return render_template('edit_review.html', form=form, review=review)


@app.route('/review/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    session_db = db_session.create_session()
    review = session_db.query(Review).filter(Review.id == review_id).first()
    if not review:
        session_db.close()
        return redirect('/')
    product_id = review.product_id
    if not current_user.is_admin() and review.user_id != current_user.id:
        session_db.close()
        return redirect(f'/product/{product_id}')

    session_db.delete(review)
    session_db.commit()
    session_db.close()
    return redirect(f'/product/{product_id}')


@app.route('/order/<int:product_id>', methods=['POST'])
@login_required
def create_order(product_id):
    quantity = int(request.form['quantity'])
    session_db = db_session.create_session()
    product = session_db.query(Product).filter(
        Product.id == product_id).first()
    if not product or product.stock < quantity:
        session_db.close()
        return redirect(f'/product/{product_id}')

    total_price = product.price * quantity
    order = Order()
    order.user_id = current_user.id
    order.product_id = product_id
    order.quantity = quantity
    order.total_price = total_price
    product.stock -= quantity
    session_db.add(order)
    session_db.commit()
    session_db.close()
    return redirect('/orders')


@app.route('/orders')
@login_required
def my_orders():
    session_db = db_session.create_session()
    orders = session_db.query(Order).filter(
        Order.user_id == current_user.id).order_by(Order.order_date.desc()).all()
    for order in orders:
        _ = order.product
    session_db.close()
    return render_template('orders.html', orders=orders)


@app.route('/seller/products')
@login_required
def seller_products():
    if not current_user.is_seller() and not current_user.is_admin():
        return redirect('/')

    session_db = db_session.create_session()
    products = session_db.query(Product).filter(
        Product.seller_id == current_user.id).all()
    for product in products:
        _ = product.images
    session_db.close()
    return render_template('seller_products.html', products=products)


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
