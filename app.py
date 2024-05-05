from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Regexp
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

# class ContactForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired()])
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     message = TextAreaField('Message', validators=[DataRequired()])
#     submit = SubmitField('Send Message')

# class ConsultForm(FlaskForm):
#     name = StringField('Name', validators=[DataRequired()])
#     phone = StringField('Phone', validators=[DataRequired(), Regexp(r'^\d{10}$', message="Invalid phone number")])
#     therapy_type = SelectField('Therapy Type', choices=[
#         ('individual', 'Individual Therapy'),
#         ('couples', 'Couples Therapy'),
#         ('family', 'Family Therapy'),
#         ('group', 'Group Therapy'),
#         ('child', 'Child Therapy'),
#         ('adolescent', 'Adolescent Therapy')
#     ], validators=[DataRequired()])
#     submit = SubmitField('Submit')

@app.route('/')
def index():
    return render_template('base.html')

# @app.route('/tips')
# def tips():
#     tips_list = [
#         {"title": "Stay Active", "description": "Exercise regularly to boost your mood."},
#         {"title": "Stay Connected", "description": "Keep in touch with family and friends."},
#         {"title": "Take Breaks", "description": "Give yourself time to relax."},
#     ]
#     return render_template('tips.html', tips=tips_list)

# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     form = ContactForm()
#     if form.validate_on_submit():
#         flash('Message sent successfully!', 'success')
#         return redirect(url_for('contact'))
#     return render_template('contact.html', form=form)

# @app.route('/therapists')
# def therapists():
#     return render_template('therapists.html')

# @app.route('/about')
# def about():
#     return render_template('about.html')

# @app.route('/consult', methods=['GET', 'POST'])
# def consult():
#     form = ConsultForm()
#     if form.validate_on_submit():
#         flash('Lead form submitted successfully!', 'success')
#         return redirect(url_for('consult'))
#     return render_template('consult.html', form=form)

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
    app.run(debug=True)