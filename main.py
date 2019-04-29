from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:myphpspencer@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = '12345'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

# # TODO create a require_login
# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'signup', 'blog', 'index']
#     if request.endpoint not in allowed_routes and 'username' not in session:
#         return redirect('/login')


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route("/signup", methods=['POST'])
def validate_signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['confirm_password']

        username_error = ''
        password_error = ''
        password_check_error = ''

        if len(username) < 3 or len(username) > 20:
            username_error = "username must contain no spaces and must be between 3 and 20 characters"
            username = ""

        if " " in password or len(password) < 3 or len(password) > 20:
            password_error = "Password must not contain spaces and must be between 3-20 characters"
            password = ''

        if not password_check == password:
            password_check_error = "That password does not match"
            password_check = ''
        elif " " in password_check or len(password_check) < 3 or len(password_check) > 20:
            password_check_error = "Password must not contain spaces and must be between 3-20 characters"
            password_check = ''
        
        if not username_error and not password_error and not password_check_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/new_entry')
            else:
                username_error = 'User already exists'
                return render_template('signup.html', username_error=username_error)

        else:
            return render_template('signup.html', password_error=password_error, password_conf_error=password_check_error, username_error=username_error, username=username)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/new_entry')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

## TODO create a / index route handler function

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/new_entry', methods=['POST', 'GET'])
def new_entry():
    title = "Add a New Entry"
    if request.method == 'POST':
        blog_title = request.form['entry_title']
        blog_body = request.form['entry_body']
        if blog_title != '' and blog_body != '':
            new_blog = Blog(blog_title, blog_body, get_logged_in_user())
            db.session.add(new_blog)
            db.session.commit()
            blog = db.session.query(Blog).order_by(Blog.id.desc()).first()
            get_id = blog.id
            return redirect('/blog?id=' + str(get_id))
        else:
            if blog_title == '':
                flash('Please fill in title field', 'title_error')
            if blog_body == '':
                flash('Please fill in entry field', 'body_error')
            return render_template('new_entry.html', title=title, entry_title=blog_title, entry_body=blog_body)


    return render_template('new_entry.html', title=title)

def get_logged_in_user():
    return User.query.filter_by(username=session['username']).first()

@app.route('/blog', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()
    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('blog_entry.html', blog=blog)
    else:
        return render_template('blog.html', title='Build A Blog', blogs=blogs)


if __name__ == '__main__':
    app.run()