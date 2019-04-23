from flask import Flask, request, redirect, render_template, flash
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

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/new_entry', methods=['POST', 'GET'])
def new_entry():
    title = "Add a New Entry"
    if request.method == 'POST':
        blog_title = request.form['entry_title']
        blog_body = request.form['entry_body']
        if blog_title != '' and blog_body != '':
            new_blog = Blog(blog_title, blog_body)
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