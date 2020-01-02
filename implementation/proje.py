from flask import Flask, render_template, flash, redirect, url_for, session, logging,request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, RadioField, IntegerField, SelectMultipleField, validators
from functools import wraps


# User Login Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You have to login", "danger")
            return redirect(url_for("login"))
    return decorated_function
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
class uploadForm(Form):
    appName = StringField("Enter app name", validators=[validators.Length(min=4, max=25)])
    ageRestriction = IntegerField("Enter age limit",validators=[validators.NumberRange(min=0, max=99)])
    size = IntegerField("Enter size in Mb", validators=[validators.NumberRange(min=0, max=99)])
    osVersion = IntegerField("Enter android version", validators=[validators.NumberRange(min=4, max=9)])
    category = StringField("Enter category", validators=[validators.Length(min=4, max=25)])

# Create App Form
class updateForm(Form):
    appName = StringField("Enter app name", validators=[validators.Length(min=4, max=25)])
    ageRestriction = IntegerField("Enter age limit",validators=[validators.NumberRange(min=0, max=99)])
    size = IntegerField("Enter size in Mb", validators=[validators.NumberRange(min=0, max=99)])
    osVersion = IntegerField("Enter android version", validators=[validators.NumberRange(min=4, max=9)])
    category = StringField("Enter category", validators=[validators.Length(min=4, max=25)])
    description = StringField("Enter description", validators=[validators.Length(min=0, max=200)])
# Approve Restriction Form
class approveRestrictionForm(Form):
    appName = StringField("Enter app name", validators=[validators.Length(min=4, max=25)])
    ageRestriction = IntegerField("Enter age limit",validators=[validators.NumberRange(min=0, max=99)])
    size = IntegerField("Enter size in Mb", validators=[validators.NumberRange(min=0, max=99)])
    osVersion = IntegerField("Enter android version", validators=[validators.NumberRange(min=4, max=9)])
    category = StringField("Enter category", validators=[validators.Length(min=4, max=25)])
    description = StringField("Enter description", validators=[validators.Length(min=0, max=200)])

# Apply Filter Form
class applyFilterForm(Form):
    ageRestriction = IntegerField("Enter age limit",validators=[validators.NumberRange(min=0, max=99),validators.DataRequired("This area cannot be blank")])
    size = IntegerField("Enter size in Mb", validators=[validators.NumberRange(min=0, max=99),validators.DataRequired("This area cannot be blank")])
    osVersion = IntegerField("Enter android version", validators=[validators.NumberRange(min=4, max=9),validators.DataRequired("This area cannot be blank")])
    category = StringField("Enter category", validators=[validators.Length(min=4, max=25),validators.DataRequired("This area cannot be blank")])

# Message Form
class messageForm(Form):
    message = TextAreaField("Enter Message", validators=[validators.Length(min=0, max=300)])

# Comment Form
class commentForm(Form):
    comment = TextAreaField("Enter Comment", validators=[validators.Length(min=0, max=300)])
# Rate Form
class rateForm(Form):
    rate = RadioField("Choose your rate", choices=[('1','Terrible'), ('2','Bad'), ('3','Okey'),('4','Good'),('5','Very Good')])
#___________________________________________________________________________________________________________________
app = Flask(__name__)
# MySQL Connection
app.secret_key = "proje"
app.config["MYSQL_HOST"] = "dijkstra.ug.bilkent.edu.tr"
app.config["MYSQL_USER"] = "arda.turkoglu"
app.config["MYSQL_PASSWORD"] = "5bCUqL34"
app.config["MYSQL_DB"] = "arda_turkoglu"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

# Upload Application
@app.route("/uploadApp", methods=["GET", "POST"])
@login_required
def upload():
    form = uploadForm(request.form)
    if request.method == "POST":
        appname = form.appName.data
        agerestriction = form.ageRestriction.data
        size = form.size.data
        osversion = form.osVersion.data
        category = form.category.data

        cursor = mysql.connection.cursor()
        query = 'insert into application values(%s,%s,CURRENT_TIMESTAMP,%s,%s,"pending",%s)'
        cursor.execute(query,(appname, session["username"],agerestriction, size, osversion))

        check = 'select * from category where category = %s'
        result = cursor.execute(check, (category.lower(),))
        if result == 0:
            categoryInsert = 'insert into category values(%s)'
            cursor.execute(categoryInsert, (category.lower(),))

        categoryQuery = 'insert into category_has values(%s, %s)'
        cursor.execute(categoryQuery, (category.lower(), appname))

        
        mysql.connection.commit()
        cursor.close()
        flash("Upload succesful,","success")
        return redirect("developer")

    return render_template("/subfiles/upload.html", form=form)

# View All Apps (DEVELOPER)
@app.route("/apps", methods=["GET", "POST"])
@login_required
def viewAllApps():
    cursor = mysql.connection.cursor()
    query = "select * from application natural join category_has where ref_account_id = %s"
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        apps = cursor.fetchall()
        return render_template("/subfiles/apps.html", apps=apps)
    else:
        return render_template("/subfiles/apps.html")

# View All Apps (USER)
@app.route("/userApps", methods=["GET", "POST"])
@login_required
def userApps():
    cursor = mysql.connection.cursor()
    query0 = "drop view if exists allApplications"
    cursor.execute(query0)
    mysql.connection.commit()
    query1 = "create view allApplications as (select * from application natural join category_has where application_status='approved' or application_status='approved_with_restrictions')"
    cursor.execute(query1)
    mysql.connection.commit()
    query = "select * from allApplications"
    result = cursor.execute(query)

    if result > 0:
        apps = cursor.fetchall()
        return render_template("/subfiles/userApps.html", apps=apps)
    else:
        return render_template("/subfiles/userApps.html")
# View Downloaded Apps (USER)
@app.route("/downApps", methods=["GET", "POST"])
@login_required
def downApps():
    cursor = mysql.connection.cursor()
    query = "select app_name,download_date from downloads where account_id =%s"
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        downApps = cursor.fetchall()
        return render_template("/subfiles/downApps.html", downApps=downApps)
    else:
        return render_template("/subfiles/downApps.html")
# View/Edit Comments (USER)
@app.route("/editComments", methods=["GET", "POST"])
@login_required
def viewComments():
    cursor = mysql.connection.cursor()
    query = "select comment_id,ref_app_name,comment,date from comment where ref_account_id =%s"
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        comments = cursor.fetchall()
        return render_template("/subfiles/editComments.html", comments=comments)
    else:
        return render_template("/subfiles/editComments.html")
# Delete Comment
@app.route("/deleteComment/<int:id>" ,methods=["GET", "POST"])
@login_required
def deleteComment(id):
    print(id)
    cursor = mysql.connection.cursor()
    query = "select * from comment where comment_id= %s"
    result = cursor.execute(query,(id,))

    if result > 0:
        deleteComm = "delete from comment where comment_id= %s"
        cursor.execute(deleteComm, (id,))
        mysql.connection.commit()
        flash("You deleted your comment","success")
        return redirect(url_for("viewComments"))
    else:
        flash("Either comment does not exist or you cannot delete it", "danger")
        return redirect(url_for("viewComments"))

# View All Users
@app.route("/users", methods=["GET", "POST"])
@login_required
def viewAllUsers():
    cursor = mysql.connection.cursor()
    query = "select account_id, age, mail from user where account_id <> %s and userType = 0"
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        users = cursor.fetchall()
        return render_template("/subfiles/viewAllUsers.html", users=users)
    else:
        return render_template("/subfiles/viewAllUsers.html")

# Followers
@app.route("/followers")
@login_required
def followers():
    cursor = mysql.connection.cursor()
    query = "select * from follows where account1 = %s" 
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        followers = cursor.fetchall()
        return render_template("/subfiles/followers.html", followers=followers)
    else:
        return render_template("/subfiles/followers.html")

# Following
@app.route("/following")
@login_required
def following():
    cursor = mysql.connection.cursor()
    query = "select * from follows where account2 = %s" 
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        followings = cursor.fetchall()
        return render_template("/subfiles/following.html", followings=followings)
    else:
        return render_template("/subfiles/following.html")

# Messages
@app.route("/messages")
@login_required
def messages():
    cursor = mysql.connection.cursor()
    query = "select account2,message,date from messages where account1 = %s group by account2,message,date" 
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        messages = cursor.fetchall()
        return render_template("/subfiles/messages.html", messages=messages)
    else:
        return render_template("/subfiles/messages.html")
# Send Message
@app.route("/message/<string:id>", methods=["GET", "POST"])
@login_required
def sendMessage(id):
    form = messageForm(request.form)

    if request.method == "POST":
        message = form.message.data
        cursor = mysql.connection.cursor()
        query = "insert into messages values(NULL,%s,%s,%s,CURRENT_TIMESTAMP)"
        
        cursor.execute(query,(id, session["username"], message,))
        mysql.connection.commit()
        flash("Message Sent", "success")
        return redirect(url_for("viewAllUsers"))
    else:
        return render_template("/subfiles/sendMessage.html", form=form)
 # Send Comment
@app.route("/comment/<string:id>", methods=["GET", "POST"])
@login_required
def sendComment(id):
    form = commentForm(request.form)

    if request.method == "POST":
        comment = form.comment.data
        cursor = mysql.connection.cursor()
        queryDown = "select * from downloads where app_name = %s and account_id =%s"
        result = cursor.execute(queryDown,(id,session["username"],))

        if result > 0:
            query = "insert into comment values(NULL,%s,%s,%s,CURRENT_TIMESTAMP)"        
            cursor.execute(query,(session["username"],id, comment,))
            mysql.connection.commit()
            flash("Comment Sent", "success")
            return redirect(url_for("userApps"))
        else:
           flash("You have to download application first.", "danger")
           return redirect(url_for("userApps"))
    else:
        return render_template("/subfiles/comment.html", form=form)
# Update Comment
@app.route("/updateComment/<string:id>", methods=["GET", "POST"])
@login_required
def updateComment(id):
    form = commentForm(request.form)

    if request.method == "POST":
        comment = form.comment.data
        cursor = mysql.connection.cursor()
        queryDown = "update comment set comment =%s where comment_id = %s"
        cursor.execute(queryDown,(comment,id,))
        mysql.connection.commit()
        flash("Comment Sent", "success")
        return redirect(url_for("viewComments"))
    else:
        return render_template("/subfiles/updateComment.html", form=form)
# Send Rate
@app.route("/rate/<string:id>", methods=["GET", "POST"])
@login_required
def sendRate(id):
    form = rateForm(request.form)

    if request.method == "POST":
        rate = form.rate.data
        cursor = mysql.connection.cursor()
        queryDown = "select * from downloads where app_name = %s and account_id =%s"
        result = cursor.execute(queryDown,(id,session["username"],))

        if result > 0:
            query = "insert into rate values(NULL,%s,%s,%s,CURRENT_TIMESTAMP)"        
            cursor.execute(query,(session["username"],id, rate,))
            mysql.connection.commit()
            flash("Rate Sent", "success")
            return redirect(url_for("userApps"))
        else:
           flash("You have to download application first.", "danger")
           return redirect(url_for("userApps"))
    else:
        return render_template("/subfiles/rate.html", form=form)
# View App Statistics
@app.route("/statistics/<string:id>", methods=["GET", "POST"])
@login_required
def viewAppStatistics(id):
    cursor = mysql.connection.cursor()
    query = "select count(app_name) as download_count from downloads where app_name = %s"
    result = cursor.execute(query,(id,))
    downs = cursor.fetchall()

    query2 = "select avg(rating) as avg_rate from rate where ref_app_name = %s"
    cursor.execute(query2,(id,))
    rates = cursor.fetchall()

    query3 = "select ref_account_id,comment,date from comment where ref_app_name = %s group by ref_account_id,comment,date"
    cursor.execute(query3,(id,))
    comments = cursor.fetchall()
    if result > 0:
        
        return render_template("/subfiles/statistics.html", downs=downs, rates=rates,comments=comments)
    else:
        return render_template("/subfiles/statistics.html")
# Follow
@app.route("/follow/<string:id>")
@login_required
def follow(id):
    cursor = mysql.connection.cursor()
    check = "select * from follows where account1 = %s and account2 = %s"
    result = cursor.execute(check,(id,session["username"]))
    
    if result > 0:
        flash("You already follow that user", "danger")
        return redirect(url_for("viewAllUsers"))
    else:
        query = "insert into follows values(%s, %s)"
        cursor.execute(query,(id,session["username"]))
        mysql.connection.commit()
        flash("Follow Success", "success")
        return redirect(url_for("viewAllUsers"))

# View Dev Requests
@app.route("/viewDevStatus")
@login_required
def viewDevStatus():
    cursor = mysql.connection.cursor()
    query = "select * from request natural join requestofapp where account_id=%s "
    result = cursor.execute(query,(session["username"],))
    

    if result > 0:
        requests = cursor.fetchall()
        return render_template("/subfiles/viewDevStatus.html", requests=requests)
    else:
        return render_template("/subfiles/viewDevStatus.html")


# View All Requests
@app.route("/requests", methods=["GET", "POST"])
@login_required
def viewAllRequests():
    cursor = mysql.connection.cursor()
    query = "select * from request natural join requestofapp where request_status='pending'"
    result = cursor.execute(query)
    

    if result > 0:
        requests = cursor.fetchall()
        return render_template("/subfiles/requests.html", requests=requests)
    else:
        return render_template("/subfiles/requests.html")

# Reject A Request
@app.route("/reject/<int:id>")
@login_required
def reject(id):
    cursor = mysql.connection.cursor()
    rejectQ = "update request set request_status='rejected' where request_id=%s"
    cursor.execute(rejectQ, (id,))
    query1 = "update application set application_status=%s where app_name=(select app_name from requestofapp where request_id=%s)"
    cursor.execute(query1, ("rejected",id,))
    mysql.connection.commit()
    flash("Request rejected", "success")
    return redirect(url_for("viewAllRequests"))

# Approve With Restrictions
@app.route("/approveRestriction/<int:id>", methods=["GET", "POST"])
@login_required
def approveRestriction(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        query = "select * from application natural join category_has where app_name = (select app_name from requestofapp where request_id=%s)"
        result = cursor.execute(query,(id,))

        if result == 0:
            flash("Either request does not exist or you cannot approve it", "danger")
            return redirect(url_for("viewAllRequest"))
        else:
            app = cursor.fetchone()
            form = approveRestrictionForm()
            form.appName.data = app["app_name"]
            form.ageRestriction.data = app["age_restriction"]
            form.size.data = app["size"]
            form.osVersion.data = app["os_version"]
            form.category.data = app["category"]
            return render_template("/subfiles/approveRestriction.html", form=form)
    else:
        cursor = mysql.connection.cursor()
        form = approveRestrictionForm(request.form)
        
        appname = form.appName.data
        newage = form.ageRestriction.data
        newsize = form.size.data
        newcat = form.category.data
        
        check = 'select * from category where category = %s'
        result = cursor.execute(check, (newcat.lower(),))
        if result == 0:
            categoryInsert = 'insert into category values(%s)'
            cursor.execute(categoryInsert, (newcat.lower(),))

        query1 = 'update application set release_date=CURRENT_TIMESTAMP, age_restriction=%s, size=%s, application_status="approved_with_restrictions" where app_name=%s'
        cursor.execute(query1, (newage,newsize,appname))

        query3 = "update category_has set category=%s where app_name =%s"
        cursor.execute(query3, (newcat.lower(),appname))

        query2 = 'update request set request_status="approved_with_restrictions" where request_id=%s'
        cursor.execute(query2, (id,))


        mysql.connection.commit()
        flash("Success", "success")
        return redirect(url_for("viewAllRequests"))

# Direct Approve
@app.route("/directApprove/<int:id>")
@login_required
def directApprove(id):
    cursor = mysql.connection.cursor()
    approvedQuery = "update request set request_status='approved' where request_id=%s"
    cursor.execute(approvedQuery, (id,))
    query1 = "update application set application_status=%s where app_name=(select app_name from requestofapp where request_id=%s)"
    cursor.execute(query1, ("approved",id,))
    mysql.connection.commit()
    flash("Request approved", "success")
    return redirect(url_for("viewAllRequests"))


# Delete App
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    query = "select * from application where ref_account_id = %s"
    result = cursor.execute(query,(session["username"],))

    if result > 0:
        deleteFromCat = "delete from category_has where app_name = %s"
        cursor.execute(deleteFromCat, (id,))

        deleteQuery = "delete from application where app_name = %s"
        cursor.execute(deleteQuery, (id,))
        mysql.connection.commit()
        return redirect(url_for("viewAllApps"))
    else:
        flash("Either app does not exist or you cannot delete it", "danger")
        return redirect(url_for("viewAllApps"))

# Update App
@app.route("/update/<string:id>", methods=["GET", "POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        query = "select * from application natural join category_has where app_name = %s"
        result = cursor.execute(query,(id,))

        if result == 0:
            flash("Either app does not exist or you cannot update it", "danger")
            return redirect(url_for("viewAllApps"))
        else:
            app = cursor.fetchone()
            form = updateForm()
            form.appName.data = app["app_name"]
            form.ageRestriction.data = app["age_restriction"]
            form.size.data = app["size"]
            form.osVersion.data = app["os_version"]
            form.category.data = app["category"]
            return render_template("/subfiles/update.html", form=form)
    else:
        cursor = mysql.connection.cursor()
        form = updateForm(request.form)
        newName = form.appName.data
        newage = form.ageRestriction.data
        newsize = form.size.data
        newos = form.osVersion.data
        newDescript = form.description.data
        newcat = form.category.data
        
        check = 'select * from category where category = %s'
        result = cursor.execute(check, (newcat.lower(),))
        if result == 0:
            categoryInsert = 'insert into category values(%s)'
            cursor.execute(categoryInsert, (newcat.lower(),))

        
        check2 = 'select * from application where app_name=%s'
        result2 = cursor.execute(check2, (newName,))
        if result2 == 0:
            query1 = "update application set  release_date=CURRENT_TIMESTAMP, age_restriction=%s, size=%s, os_version=%s"
            cursor.execute(query1, (newage,newsize,newos))

        query3 = "update category_has set category=%s where app_name=%s"
        cursor.execute(query3, (newcat,newName))

        query2 = "insert into request values(NULL,%s, %s, %s)"
        cursor.execute(query2, (session["username"], "pending", newDescript))

        query4 = "insert into requestofapp values(%s, NULL)"
        cursor.execute(query4, (newName,))

        

        mysql.connection.commit()
        flash("Update successful", "success")
        return redirect(url_for("viewAllApps"))

            
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
        
        cursor.execute(query,(username, password, int(age), name, email, userType))
        
        if userType == "1":
            queryDeveloper = "insert into developer values(%s)"
            cursor.execute(queryDeveloper, (username,))
            
        if userType == "2":
            queryEditor = "insert into editor values(%s)"
            cursor.execute(queryEditor, (username,))
            
        mysql.connection.commit()
        cursor.close()

        deviceParse(username, device)

        flash(u"Register successful, you can login", "success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html", form=form)



# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
   
    if request.method == "POST":
        
        username = form.username.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        query = "select * from user where account_id = %s and password = %s"
        result = cursor.execute(query, (username,password))

        if result > 0:
            
            data = cursor.fetchone()
            
            if data["userType"] == 0:
                flash(u"Login Successful", "success")
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("user"))
            if data["userType"] == 1:
                flash(u"Login Successful", "success")
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("developer"))
            if data["userType"] == 2:
                flash(u"Login Successful", "success")
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("editor"))
            
        else:
            flash(u"Username or password wrong", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)

def deviceParse(username,device):
    myList = device.split(",")
    cursor = mysql.connection.cursor()
    for i in myList:
        myList2 = i.split("-")
        query = "insert into device values(%s, %s, %s)"
        cursor.execute(query,(myList2[0].lower(), username, myList2[1]))
        mysql.connection.commit()
    cursor.close()

# User Page
@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    return render_template("user.html")

# Developer Page
@app.route("/developer", methods=["GET", "POST"])
@login_required
def developer():
    return render_template("developer.html")

# Editor Page
@app.route("/editor", methods=["GET", "POST"])
@login_required
def editor():
    return render_template("editor.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Download App
@app.route("/download/<string:appName>")
@login_required
def download(appName):
    cursor = mysql.connection.cursor()
    query = "select * from  application A, user U where account_id=%s and U.age >= A.age_restriction and A.app_name = %s"
    result = cursor.execute(query, (session["username"],appName,))

    if result > 0:
        queryOs = "select * from  device D, application A where D.user_id=%s and D.os_version >= A.os_version and A.app_name = %s"
        resultos = cursor.execute(queryOs, (session["username"],appName,))
        if resultos > 0:


            downloadCheck = "select * from downloads where app_name = %s and account_id = %s"
            result2 = cursor.execute(downloadCheck, (appName, session["username"],))

            if result2 == 0:
                downloadQuery = "insert into downloads values(%s, %s, CURRENT_TIMESTAMP)"
                cursor.execute(downloadQuery, (appName,session["username"],))
                mysql.connection.commit()
                flash("Download Successful", "success")
                return redirect(url_for("userApps"))
            else:
                flash("You have already downloaded", "info")
                return redirect(url_for("userApps"))
        else:
            flash("You cannot download this application to your device.","danger")
            return redirect(url_for("userApps"))
    else:
        flash("Your age does not fit to download this application.", "danger")
        return redirect(url_for("userApps"))

#Apply Filter
@app.route("/applyFilter", methods=["GET", "POST"])
def applyFilter():
    form = applyFilterForm(request.form)

    if request.method == "POST":
        size = form.size.data
        category = form.category.data
        age = form.ageRestriction.data
        os_version = form.osVersion.data
        

        cursor = mysql.connection.cursor()
        query = "select * from application natural join category_has where size <= %s and age_restriction <=%s and category=%s and os_version <= %s"
        
        result = cursor.execute(query,(size, int(age), category, os_version,))
        
        if result > 0:
            filters = cursor.fetchall()
            flash("Filter applied", "success")
            return render_template("/subfiles/filter.html", filters=filters)
            
        else:
            flash("No Result", "danger")
            return render_template("/subfiles/applyFilter.html", form=form)
            
    else:
        return render_template("/subfiles/applyFilter.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)