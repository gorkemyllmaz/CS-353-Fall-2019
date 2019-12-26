from flask import Flask, render_template,flash, redirect, url_for, session, logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators

# Register Form
class RegisterForm(Form):
    name = StringField("Name Lastname", validators=[validators.Length(min=4, max=25)])
    username = StringField("Username", validators=[validators.Length(min=5, max=35)])
    email = StringField("Email", validators=[validators.Email(message="Please use a proper Email address")])
    password = PasswordField("Password", validators=[validators.DataRequired("Please enter a password")])
# Login Form
class LoginForm(Form):
    username = StringField("Username")
    password = PasswordField("Password")
#___________________________________________________________________________________________________________________
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/user")
def user():
    return render_template("user.html")

#Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST":
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    return render_template("login.html", form=form)
if __name__ == "__main__":
    app.run(debug=True)