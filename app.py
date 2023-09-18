from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import secrets
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField, RadioField, EmailField, DateTimeField)
from wtforms.validators import InputRequired, Email, EqualTo, Length
import pymongo
import json
from flask_mail import Mail, Message


# json.load() convert json into dictionary and json.loads() convert json string into dictionary
with open('templates/config.json', 'r') as f:
    config = json.load(f)


app = Flask(__name__)


# app.config['MAIL_SERVER']='smtp.gmail.com'
# app.config['MAIL_PORT'] = '465'
# app.config['MAIL_USERNAME'] = config["mail"]["your_mail"]
# app.config['MAIL_PASSWORD'] = config["mail"]["Email_Password"]
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)

key =secrets.token_hex(12)
app.secret_key = key

class RegForm(FlaskForm):
    Username = StringField('Username', validators=[InputRequired(),
                                             Length(min=5, max=20)])
    Phone_Number = StringField('Phone_Number',
                                validators=[InputRequired()])
    Email = EmailField('Email', validators=[InputRequired()])
    Password = StringField('Password',
                       validators=[InputRequired()])
    Confirm_Password = StringField('Confirm_Password', validators=[InputRequired(), 
                                                                   EqualTo('Password', message="password must match")])
    
class LoginForm(FlaskForm):
    Username = StringField('Username', validators=[InputRequired(),
                                             Length(min=5, max=20)])
    Password = StringField('Password',validators=[InputRequired()])
    
class Books(FlaskForm):
    Username = StringField('Username', validators=[InputRequired(),
                                             Length(min=5, max=20)])
    Id = StringField("Id", validators=[InputRequired()])
    Title = StringField('Title', validators=[InputRequired(),
                                             Length(min=5, max=20)])
    Author = StringField('Author',validators=[InputRequired()])


# setup a mongodb database

from pymongo import MongoClient
client = MongoClient("localhost", 27017)
db = client["library"]
users = db["info"]
#making another database
query = db["random_user"]
books = db["books"]


#Routing

@app.route("/", methods = ["GET","POST"])
@app.route("/home", methods = ["GET","POST"])
def home():
    if request.method == "POST":
        data={}
        data["Name"]= request.form["Name"]
        data["Email"]= request.form["Email"]
        data["Subject"]= request.form["Subject"]
        data["Message"]= request.form["Message"]

        db.query.insert_one(data)
        flash("Thanks for Connecting Us !")

        return redirect(url_for('login'))

    return render_template('home.html')
    
@app.route("/<string:usr>", methods = ["GET","POST"])
def user(usr):
    book_list = db.books.find({"Username":usr})
    return render_template('user.html', book_list=book_list, usr= usr)

@app.route("/login/", methods= ["POST","GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        present = db.users.find_one({"Username":request.form['Username']})
        if present != None and present["Password"] == request.form["Password"]:
            flash("Welcome {} !".format(request.form["Username"]))
            return redirect(url_for('user', usr = request.form["Username"]))
        elif present != None:
            flash("Wrong Password !")
            return redirect(url_for('login'))
        else:
            flash("Try to register First !")
            return redirect(url_for('register'))

    else:
        return render_template('/login/index.html', form = form)


@app.route("/Students/")
def Students():
    stud_all = db.users.find({})
    return  render_template('Students.html', stud_all = stud_all)

@app.route("/register/", methods = ["POST", "GET"])
def register():
    form = RegForm()
    if request.method == "POST" and form.validate_on_submit():
        if db.users.find_one({"Email": request.form["Email"]}) == None:
            new_usr = {}
            new_usr["Username"] = request.form.get('Username')
            new_usr['Phone_Number'] = request.form.get('Phone_Number')
            new_usr['Email'] = request.form.get('Email')
            new_usr['Password'] = request.form.get('Password')
            new_usr['Confirm_Password'] = request.form.get('Confirm_Password')

            db.users.insert_one(new_usr)
            flash("User Successfully Registered !")
            print("got it")
            return redirect(url_for('login'))
        else:
            flash("User already registered !")
            return redirect(url_for('login'))
        
    else:
         return render_template('register.html', form = form)


@app.route('/admin/', methods= ["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["Username"] == "admin" and request.form["Password"] == "admin":
            flash("Welcome Admin !")
            return "hi"
        else:
            flash("Wrong Credentials")
            return redirect(url_for('admin'))
    else:
        return render_template('admin_login.html')

    





if __name__ == "__main__":
    app.run(debug=True)
