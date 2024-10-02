from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="blog_database"
)

@app.route('/')
def index():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM blogs ORDER BY date_posted DESC")
    blogs = cursor.fetchall()
    cursor.close()
    return render_template('index.html', blogs=blogs)

@app.route('/post/<int:blog_id>')
def view_post(blog_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM blogs WHERE id = %s", (blog_id,))
    blog = cursor.fetchone()
    
    cursor.execute("SELECT * FROM comments WHERE blog_id = %s", (blog_id,))
    comments = cursor.fetchall()
    cursor.close()
    
    return render_template('view_post.html', blog=blog, comments=comments)

@app.route('/new_blog', methods=['GET', 'POST'])
def new_blog():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date_posted = request.form['date_posted']
        
        cursor = db.cursor()
        query = "INSERT INTO blogs (title, content, date_posted) VALUES (%s, %s, %s)"
        cursor.execute(query, (title, content, date_posted))
        db.commit()
        cursor.close()
        
        return redirect(url_for('index'))
    return render_template('new_blog.html')

@app.route('/comment/<int:blog_id>', methods=['POST'])
def add_comment(blog_id):
    username = request.form['username']
    comment = request.form['comment']
    date_posted = datetime.now().strftime('%Y-%m-%d')
    
    cursor = db.cursor()
    query = "INSERT INTO comments (blog_id, username, comment, date_posted) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (blog_id, username, comment, date_posted))
    db.commit()
    cursor.close()
    
    return redirect(url_for('view_post', blog_id=blog_id))

@app.route('/filter', methods=['POST'])
def filter_posts():
    filter_option = request.form['filter_option']
    cursor = db.cursor(dictionary=True)
    
    if filter_option == 'days':
        date_limit = datetime.now() - timedelta(days=7)
    elif filter_option == 'weeks':
        date_limit = datetime.now() - timedelta(weeks=4)
    elif filter_option == 'months':
        date_limit = datetime.now() - timedelta(weeks=12)
    
    query = "SELECT * FROM blogs WHERE date_posted >= %s ORDER BY date_posted DESC"
    cursor.execute(query, (date_limit,))
    blogs = cursor.fetchall()
    cursor.close()
    
    return render_template('index.html', blogs=blogs)

if __name__ == '__main__':
    app.run(debug=True)
