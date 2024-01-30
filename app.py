from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'Flasky123@'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = 1)
    name = db.Column(db.String(80), nullable = 0)
    email = db.Column(db.String(80), nullable = 0, unique = 1)
    password = db.Column(db.String(80), nullable = 0)


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=40), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    name = HiddenField(id="fullname")
    email = StringField(validators=[InputRequired(), Length(min=4, max=40), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_email(self, email):
        user_exists = User.query.filter_by(email = email.data).first()
        if user_exists: raise ValidationError("email already taken.")



@app.route('/')
def homepage():   
    return render_template('index.html')


@app.route('/crops')
def crops():
    return render_template('crops.html')


@app.route('/fertilizers')
def fertilizers():
    return render_template('fertilizers.html')


@app.route('/disease')
def disease():
    return render_template('disease.html')



@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name = form.name.data, email = form.email.data, password = hashed_pwd)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('signup.html', form=form)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect('/')

    return render_template('login.html', form=form)


@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def user():
    return "user dashboard"



@app.route('/cropsResult', methods = ['GET', 'POST'])
def cropsResult():
    if request.method == 'POST':
        print(request.form)
    
    return 'crops result page'


@app.route('/fertilizersRequired', methods = ['GET', 'POST'])
def requiredFertilizers():
    if request.method == 'POST':
        print(request.form)
    
    return 'Required Fertilizers result page'


@app.route('/diseasePredictor', methods = ['GET', 'POST'])
def predictDisease():
    if request.method == 'POST':
        print(request.form)
    
    return 'Predicted Disease result page'



if __name__ == "__main__" : app.run(debug=True, port=3000)