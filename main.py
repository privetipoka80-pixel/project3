from flask import request, redirect, url_for
from forms.forms import RegistrationForm, LoginForm
from data.users import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template
import data.db_session as db_session
from data.products import Product

db_session.global_init('db/shop.db')

app = Flask(__name__)
app.secret_key = 'dev_secret_key_123'


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


if __name__ == '__main__':
    app.run(debug=True, port=8080)
