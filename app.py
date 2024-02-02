from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt

import numpy as np
import pandas as pd
import sklearn
import pickle

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



@app.route('/cropsResult', methods = ['POST'])
def cropsResult():
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

        print("crop prediction")
        print("-------------------------------")
        print("input data -> ", features[0])

        crop_idx = {
            1: 'rice',
            2: 'maize',
            3: 'chickpea',
            4: 'kidneybeans',
            5: 'pigeonpeas',
            6: 'mothbeans',
            7: 'mungbean',
            8: 'blackgram',
            9: 'lentil',
            10: 'pomegranate',
            11: 'banana',
            12: 'mango',
            13: 'grapes',
            14: 'watermelon',
            15: 'muskmelon',
            16: 'apple',
            17: 'orange',
            18: 'papaya',
            19: 'coconut',
            20: 'cotton',
            21: 'jute',
            22: 'coffee'
        }

        crop_url = {
            'rice' : 'https://images.cnbctv18.com/wp-content/uploads/2023/07/Rice-2.jpg',
            'maize' : 'https://seed2plant.in/cdn/shop/products/maizeseeds.jpg?v=1604034397',
            'chickpea' : 'https://media.post.rvohealth.io/wp-content/uploads/2021/10/chickpeas-732x549-thumbnail-732x549.jpg',
            'kidneybeans' : 'https://media.istockphoto.com/id/1863013813/photo/dried-raw-red-beans-in-a-bowl.webp?b=1&s=170667a&w=0&k=20&c=TY4zeXBm8iK415Rk-IlXTGxNeV7vGQ0laPPPQa8a8uQ=',
            'pigeonpeas' : 'https://5.imimg.com/data5/SELLER/Default/2021/11/HW/CP/XB/10888193/pigeon-pea-seeds.jpg',
            'mothbeans' : 'https://www.poshtik.in/cdn/shop/products/Moth_Dal_Poshtik_grande.jpg?v=1565272395',
            'mungbean' : 'https://www.cookingwithcamilla.com/wp-content/uploads/2022/11/whole-green-mung-beans-1x1-2369.jpg',
            'blackgram' : 'https://www.shutterstock.com/image-photo/fresh-black-gram-udad-clay-600nw-2077914544.jpg',
            'lentil' : 'https://www.keepingthepeas.com/wp-content/uploads/2022/11/red-lentils-in-wood-bowl.jpg',
            'pomegranate' : 'https://insanelygoodrecipes.com/wp-content/uploads/2023/02/Cut-Opened-Ripe-Pomegranate-on-Wood-Plate.jpg',
            'banana' : 'https://www.forbesindia.com/media/images/2022/Sep/img_193773_banana.jpg',
            'mango' : 'https://img.etimg.com/thumb/width-640,height-480,imgsize-105444,resizemode-75,msid-91803294/small-biz/trade/exports/insights/a-heat-waves-lamented-victim-the-mango-indias-king-of-fruits/mango-stock.jpg',
            'grapes' : 'https://images.pexels.com/photos/9556561/pexels-photo-9556561.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
            'watermelon' : 'https://hips.hearstapps.com/hmg-prod/images/fresh-ripe-watermelon-slices-on-wooden-table-royalty-free-image-1684966820.jpg',
            'muskmelon' : 'https://www.healthshots.com/wp-content/uploads/2020/04/muskmelon.jpg',
            'apple' : 'https://images.everydayhealth.com/images/diet-nutrition/apples-101-about-1440x810.jpg',
            'orange' : 'https://www.heythattastesgood.com/wp-content/uploads/2022/06/orange-fruits.jpg',
            'papaya' : 'https://draxe.com/wp-content/uploads/2018/11/DrAxePapayaBenefitsHeader.jpg',
            'coconut' : 'https://cdn11.bigcommerce.com/s-i52r9dz4cm/products/1780/images/1382/CO-635_Coconut_Oil__47403.1581876884.500.750.jpg?c=2',
            'cotton' : 'https://imgix-prod.sgs.com/-/media/sgscorp/images/natural-resources/cotton-plant.cdn.en-IN.1.jpg?fit=crop&crop=edges&auto=format&w=1200&h=630',
            'jute' : 'https://researchoutreach.org/wp-content/uploads/2021/05/shutterstock_1340391350.jpg',
            'coffee' : 'https://5.imimg.com/data5/SELLER/Default/2021/8/AP/WL/GJ/5504430/roasted-coffee-beans-500x500.jpg'
        }

        if len(predict) > 0:
            res = []
            res_url = []
            for i in predict: 
                res.append(crop_idx[i])
                res_url.append(crop_url[crop_idx[i]])

            print("Output -> ", res)
            print("-------------------------------")
            return render_template('crops.html', result = True, data = [res, res_url])
        else:
            return render_template('crops.html', result = True, data = "-1")

    return render_template('crops.html', result = False)


@app.route('/fertilizersRequired', methods = ['GET', 'POST'])
def requiredFertilizers():
    if request.method == 'POST':
        pass
    
    return 'Required Fertilizers result page'


@app.route('/diseasePredictor', methods = ['GET', 'POST'])
def predictDisease():
    if request.method == 'POST':
        print(request.form)
    
    return 'Predicted Disease result page'



if __name__ == "__main__" : app.run(debug=True, port=3000)