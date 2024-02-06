from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt
from markupsafe import Markup

import numpy as np
import pandas as pd
import sklearn
import pickle

from utils.data import crop_idx, crop_url, fertilizer_data


crops_model = pickle.load(open('./models/crops.pkl', 'rb'))

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
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')
    return render_template('index.html', lang = lang)


@app.route('/crops')
def crops():
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')
    return render_template('crops.html', lang = lang)


@app.route('/fertilizers')
def fertilizers():
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')
    return render_template('fertilizers.html', lang = lang)


@app.route('/disease')
def disease():
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')
    return render_template('disease.html', lang = lang)



@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    form = RegistrationForm()

    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')

    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name = form.name.data, email = form.email.data, password = hashed_pwd)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('signup.html', form = form, lang = lang)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect('/')

    return render_template('login.html', form = form, lang = lang)


@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def user():
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')
    return render_template("dashboard.html", lang = lang)



@app.route('/cropsResult', methods = ['POST'])
def cropsResult():
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')

    if request.method == 'POST':
        n = float(request.form['nitrogen'])
        p = float(request.form['phosphorus'])
        k = float(request.form['potassium'])
        temp = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['pH'])
        rainfall = float(request.form['rainfall'])

        features = np.array([[n, p, k, temp, humidity, ph, rainfall]])
        predict = crops_model.predict(features)

        # print("crop prediction")
        # print("-------------------------------")
        # print("input data -> ", features[0])
        
        if len(predict) > 0:
            res = []
            res_url = []
            for i in predict: 
                res.append(crop_idx[i])
                res_url.append(crop_url[crop_idx[i]])

            # print("Output -> ", res)
            # print("-------------------------------")
            return render_template('crops.html', result = True, data = [res, res_url], lang = lang)
        else:
            return render_template('crops.html', result = True, data = "-1", lang = lang)

    return render_template('crops.html', result = False, lang = lang)


@app.route('/fertilizersRequired', methods = ['GET', 'POST'])
def requiredFertilizers():

    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')

    if request.method == 'POST':
        n = int(request.form['nitrogen'])
        p = int(request.form['phosphorus'])
        k = int(request.form['potassium'])
        crop = request.form['cropName']

        fert = pd.read_csv('./data/fertilizer.csv')

        nitro = fert[fert['Crop'] == crop]['N'].iloc[0]
        phos = fert[fert['Crop'] == crop]['P'].iloc[0]
        pota = fert[fert['Crop'] == crop]['K'].iloc[0]

        n = abs(nitro - n)
        p = abs(phos - p)
        k = abs(pota - k)

        data = {
            n : "N",
            p : "P",
            k : "K"
        }

        maxx = data[max(data.keys())]

        if maxx == "N":
            if n < 0: key = 'NHigh'
            else: key = "Nlow"
        elif maxx == "P":
            if p < 0: key = 'PHigh'
            else: key = "Plow"
        else: 
            if k < 0: key = 'KHigh'
            else: key = "Klow"

        response = Markup(str(fertilizer_data[key]))

        return render_template('fertilizers.html', result = True, data = response, lang = lang)
    
    return render_template('fertilizers.html', result = False, lang = lang)


@app.route('/diseasePredictor', methods = ['GET', 'POST'])
def predictDisease():
    lang = 'English' if request.args.get('lang') == None else request.args.get('lang')

    if request.method == 'POST':
        print(request.form)
    
    return 'Predicted Disease result page'



if __name__ == "__main__" : app.run(debug=True, port=3000)