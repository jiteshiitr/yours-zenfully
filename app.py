from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog-details-<path:blog_id>')
def blogdetails(blog_id):
    template_address = 'blogs/blog-details-' + blog_id + '.html'
    return render_template(template_address)

base_dir=os.getcwd()
print(base_dir)
assets_dir = base_dir + '/assets'

@app.route('/assets/<path:filename>')
def serve_css(filename):
    return send_from_directory(assets_dir, filename)

@app.route('/sitemap.xml')
def serve_xml():
    return send_from_directory(base_dir, 'sitemap.xml')

if __name__ == '__main__':
    app.run(port=8000, debug=True)