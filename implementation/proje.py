from flask import Flask, render_template,flash, redirect, url_for, session, logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, RadioField, IntegerField, SelectMultipleField, validators

# Register Form
class RegisterForm(Form):
    name = StringField("Name Lastname", validators=[validators.Length(min=4, max=25)])
    username = StringField("Username", validators=[validators.Length(min=5, max=35)])
    email = StringField("Email", validators=[validators.Email(message="Please use a proper Email address")])
    password = PasswordField("Password", validators=[validators.DataRequired("Please enter a password")])
    age = IntegerField("Enter your age (0-99)", validators=[validators.NumberRange(min=0, max=99)])
    device = StringField("Enter your devices and android OS separated with comma(e.g Samsung-4,Xiaomi-9)", validators=[validators.DataRequired("This area cannot be blank")])
    
    userType = RadioField("User Type", choices=[('0','User'), ('1','Developer'), ('2','Editor')])
    
# Login Form
class LoginForm(Form):
    username = StringField("Username")
    password = PasswordField("Password")

# Create App Form
class createAppForm(Form):
    pass
#___________________________________________________________________________________________________________________
app = Flask(__name__)
# MySQL Connection
app.config["MYSQL_HOST"] = "dijkstra.ug.bilkent.edu.tr"
app.config["MYSQL_USER"] = "arda.turkoglu"
app.config["MYSQL_PASSWORD"] = "5bCUqL34"
app.config["MYSQL_DB"] = "arda_turkoglu"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

#Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        age = form.age.data
        device = form.device.data
        userType = form.userType.data

        cursor = mysql.connection.cursor()
        query = "insert into user values(%s,%s,%s,%s,%s,%s)"
        
        cursor.execute(query,(name,username,email,password,int(age),userType))
        mysql.connection.commit()
        cursor.close()

        deviceParse(username, device)

        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    return render_template("login.html", form=form)





def deviceParse(username,device):
    myList = device.split(",")
    cursor = mysql.connection.cursor()
    for i in myList:
        myList2 = i.split("-")
        query = "insert into Device values(%s, %s)"
        cursor.execute(query,(myList2[0].lower(), myList2[1]))
        mysql.connection.commit()
    cursor.close()

    



if __name__ == "__main__":
    app.run(debug=True)