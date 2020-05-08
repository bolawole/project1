import os

from flask import Flask, session, render_template,request,flash,redirect,url_for,g
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import SignUpForm,LoginForm
app = Flask(__name__)
app.config['SECRET_KEY']='1c59de0f14fddb79'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#database area

@app.route("/",methods=['GET','POST'])
@app.route("/home",methods=['GET','POST'])
def index():
    data=db.execute("SELECT * FROM users").fetchall()
    print(data)
    return render_template("home.html")


@app.before_request
def before_request():
    g.user=None
    if 'user_id' in session:
        data=db.execute("SELECT * FROM users").fetchall()
        for each_user in data:
            if each_user.id==session['user_id']:
                g.user=each_user
                break
        

@app.route("/login",methods=['GET','POST'])
def login():
    session.pop('user_id',None)
    form=LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        data=db.execute("SELECT * FROM users WHERE (username LIKE :username) AND (password LIKE :password)",{"username":username,"password":password,}).fetchone()
        print(data)
        print(username)
        if data==None:
            flash(f'Login invalid! Please check you input a correct username and password','danger')
            return render_template("log-in.html",form=form)
        else:
            session['user_id']=data.id
            flash(f'account login','success')
            return redirect(url_for('profile'))
            
        #takes the user to their account page
    return render_template("log-in.html",form=form)
    
   # data=db.execute("SELECT * FROM users").fetchall()
    #print(data)
    # if a post request was made instead of a GET request
    #if request.method=='POST':
       # username=request.form.get("username")
       # password=request.form.get("password")
       # data=db.execute("SELECT * FROM users WHERE (username LIKE :username) AND (password LIKE :password)",{"username":username,"password":password,}).fetchone()
       # print(data)
       # if data==None:
       #     flash(f'Login invalid! Please check you input a correct password','danger')
       #     return render_template("log-in.html")

       # flash(f'account login','success')
        # takes the user to their account page
        #return redirect(url_for('usersession',name=username))

    #else:
    #    return render_template("log-in.html")
   



@app.route("/Signup",methods=['GET','POST'])
def SignUp():
    form=SignUpForm()
    if form.validate_on_submit():
        password=form.password.data
        username=form.username.data
        email=form.email.data
        #insert the new credential into the database and saves it
        db.execute("INSERT INTO users(username,email,password) VALUES (:username,:email,:password)",{"username":username,"email":email,"password":password})
        db.commit()
        flash(f'Your account has been created You can now Log In','success')
        return redirect(url_for('login'))
    return render_template("sign-up.html",form=form)



    # if a post request was made instead of a GET request
   #if request.method=='POST':
      #  username=request.form.get("name")
       # email=request.form.get("email")
        #password=request.form.get("psw")
        #password_rpt=request.form.get("psw-repeat")
        #if password ==password_rpt:
         #   flash(f'Account Created Please Login','success') #flash used to display message temporarily on the screen
            # insert the new credential into the database and saves it
          #  db.execute("INSERT INTO users(username,email,password) VALUES (:username,:email,:password)",{"username":username,"email":email,"password":password})
           # db.commit()
            #return redirect(url_for('login'))
        #else:
         #   flash('SignUp Unsuccesful! Please check you input a correct password','danger')
          #  data=db.execute("SELECT * FROM users").fetchall()
           # print(data)
    #return render_template("sign-up.html")
    
@app.route("/profile",methods=['GET', 'POST'])
def profile():
    count=0
    logout=True
    if g.user==None:
        flash('Page Forbidden Login into your account to view','danger')
        return redirect(url_for('login'))
    if request.method=="POST":
        result_search=request.form.get('search')
        data=db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{result_search}%' OR title LIKE '%{result_search.title()}%' OR author LIKE '%{result_search.title()}%' OR year LIKE '%{result_search}%'").fetchall()
        for each_data in data:
            count+=1
        if data==None or data==[]:
           print(f"number of returned result is {count}")
           return render_template("user.html",message="Your Result was not found!",logout=logout) 
        print(f"number of returned result is {count}")
        return render_template("user.html",datas=data,logout=logout,count=count)

    return render_template("user.html",logout=logout)#post=session["posts"])

@app.route("/logout")
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route("/books",methods=['GET', 'POST'])
def books():
    if request.method=='POST':
        isbn=request.form.get("isbn")
        title=request.form.get("title")
        author=request.form.get("author")
        year=request.form.get("year")

        data=db.execute("SELECT * FROM books where isbn LIKE :isbn AND title LIKE :title AND author LIKE :author AND year LIKE :year ",{"isbn":isbn,"title":title,"author":author,"year":year},).fetchone()
        return render_template("review.html",data=data)
   
    return render_template("my-books.html")

@app.route("/<string:name>/<string:id>",methods=['GET'])
def review(name,id):
    logout=True
    if g.user==None:
        flash('Login to View this page','danger')
        return redirect(url_for('login'))
    data=db.execute(f"SELECT isbn,author,year FROM books WHERE title='{name}'").fetchone()
    print(data.isbn)
    return render_template("review.html",logout=logout,name=name,isbn=data.isbn,year=data.year,author=data.author)
