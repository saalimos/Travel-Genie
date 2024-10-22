from flask import Flask, render_template,request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from sqlalchemy.sql import func
from os import path
from werkzeug.utils import secure_filename
import requests

app=Flask(__name__)
db = SQLAlchemy()
DB_NAME='database.db'

app.config['SECRET_KEY'] = 'katsuren'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config["TEMPLATES_AUTO_RELOAD"] = True

def create_database(app):
    db.init_app(app)
    if not path.exists(DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(150))
    email=db.Column(db.String(150), unique=True)
    password=db.Column(db.String(150))
    tokens=db.Column(db.Integer,default=100)


class Orders(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    usermail=db.Column(db.String(150))
    name=db.Column(db.String(100), unique=True)
    orderdate=db.Column(db.String(20))
    recievedate=db.Column(db.String(20))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), unique=True)
    tag=db.Column(db.String(20), unique=True)
    image=db.Column(db.String(100), unique=True)
    price=db.Column(db.Integer)
    desc=db.Column(db.String(1000))
    sellermail=db.Column(db.String(100))

class Reviews(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    usermail=db.Column(db.String(150))
    productname=db.Column(db.String(100))
    rev=db.Column(db.String(1000))
    date=db.Column(db.DateTime(timezone=True), default=func.now())
    stars=db.Column(db.Integer)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                login_user(user, remember=True)
                return redirect('/')
            else:
                print('Wrong pass')

    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        name=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('pass')
        cpassword=request.form.get('cpass')

        check=User.query.filter_by(email=email).first()
        if check:
            return redirect('/login')
        if len(password) < 6:
            return redirect('/login')
        if password != cpassword:
            return redirect('/login')
        new_user=User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect('/')

    return redirect('/login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/product',methods=['POST'])
def product():
    productname=request.form.get('productname')
    product=Product.query.filter_by(name=productname).first()
    reviews=Reviews.query.filter_by(productname=productname)
    return render_template('single-product.html',product=product,reviews=reviews,user=current_user)


@app.route('/')
@login_required
def home():
    return render_template('home.html',user=current_user)




@app.route('/about')
def About():
    return render_template('about.html',user=current_user)


@app.route('/contact')
def Contact():
    return render_template('contact.html',user=current_user)



@app.route('/ai', methods=['GET','POST'])
def tripplanner(): 
    if request.method=="POST":
        days=request.form.get('days')
        place=request.form.get('place')
        print(days,place)
        url = "https://ai-trip-planner.p.rapidapi.com/"
        querystring = {"days":days,"destination":place}

        headers = {
            "X-RapidAPI-Key": '5bf4e0a737msh93302cb4d5a9fa7p10204ejsna242eb903318',
            "X-RapidAPI-Host": "ai-trip-planner.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        nurl = "https://real-time-image-search.p.rapidapi.com/search"

        nquerystring = {"query":f"{place}","size":"medium","safe_search":"true","region":"us"}

        nheaders = {
            'X-RapidAPI-Key': '3a0b5dd366mshdc8942750b80c04p11ba89jsndee9f6ec1288',
            'X-RapidAPI-Host': 'real-time-image-search.p.rapidapi.com'
        }

        nresponse = requests.get(nurl, headers=nheaders, params=nquerystring)

        print(nresponse)
        return render_template('ai.html',resp=response.json()['plan'],imgs=nresponse.json()['data'])


create_database(app)
app.run(debug=True)
