from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user,  current_user, logout_user,  login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config["SECRET_KEY"]= os.urandom(24)
db=SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(30),nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime,nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30), unique= True)
    password = db.Column(db.String(12))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods =["GET", "POST"])
# @login_required # ログインしている人のみアクセス
def index():
    if current_user.is_authenticated:
        if request.method == "GET":
            posts = Post.query.all()
            return render_template('index.html', posts = posts)
        
        
        else:
            title =request.form.get("title")
            detail =request.form.get("detail")
            due =request.form.get("due")

            due = datetime.strptime(due, "%Y-%m-%d")
            new_post = Post(title= title, detail = detail, due =due)

            db.session.add(new_post)
            db.session.commit()
            
            return redirect("/")
        
    if not current_user.is_authenticated:
        return redirect('/login')

@app.route('/signup', methods =["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User(username = username, password = generate_password_hash(password, method="sha256"))
        
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")

@app.route('/login', methods =["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username = username).first()
        
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required # ログインしている人のみアクセス
def logout():
    logout_user()
    return redirect("/login")




@app.route('/create')
@login_required # ログインしている人のみアクセス
def create():
    return render_template('create.html')



@app.route('/detail/<int:id>')
@login_required # ログインしている人のみアクセス
def read(id):
    post = Post.query.get(id)
    return render_template('detail.html', post=post)

@app.route('/update/<int:id>',methods = ["GET", "POST"])
@login_required # ログインしている人のみアクセス
def update(id):
    post = Post.query.get(id)
    if request.method == "GET":
        return render_template("update.html", post = post)
    else:
        post.title = request.form.get("title")
        post.detail = request.form.get("detail")
        post.due = datetime.strptime(request.form.get("due"), "%Y-%m-%d")

        db.session.commit()
        return redirect("/")

@app.route('/delite/<int:id>')
@login_required # ログインしている人のみアクセス
def delite(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect("/")

if __name__=='__main__':
    app.run(debug=True)