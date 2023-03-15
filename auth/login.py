from flask import Blueprint, render_template, url_for, redirect, session, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from werkzeug.security import check_password_hash

from db.db import get_data

import os

from dotenv import load_dotenv



#INITIALIZATION
load_dotenv()

bp_login = Blueprint('bp_login_form', __name__, template_folder='templates')

db_path = (os.getcwd() + '/db_folder/' + str(os.getenv('DB_NAME')))

table_name = 'users'



#ROUTES
@bp_login.route('/login', methods=["GET", "POST"])
@bp_login.route('/login/', methods=["GET", "POST"])
def login():
    
    login_form = Login()
    
    if login_form.validate_on_submit():
        
        login_values = ['email', 'hash_password', 'username']
        login_db_query = get_data(login_values, db_path, table_name)
        
        login_email = login_form.email.data
        login_password = login_form.password.data    
        
        
        for email, hash, user in login_db_query:
            
            if email == login_email:
                
                if check_password_hash(hash, login_password):
                    
                    session[f'logged_in_{user}'] = True
                    flash('Brawo zostałeś zalogowany')
                    
                    return redirect(url_for('bp_login_form.login_user', user=user))
                    
                else:
                    
                    print('Niepoprawne hasło')
                    return redirect(url_for('bp_auth_form.reg_no_ok'))
            
            else:
                
                print('Niepoprawny adres email.')
                return redirect(url_for('bp_auth_form.reg_no_ok'))
                            
    if request.method == 'POST':
        
        user_db_query = get_data('username', db_path, table_name)
        
        return redirect(url_for('bp_login_form.login'), user=user_db_query)
        
    return render_template('login.html', login_form=login_form)



@bp_login.route('/<user>', methods=['GET', 'POST'])
@bp_login.route('/<user>/', methods=['GET', 'POST'])
def login_user(user):
    
    if session.get(f'logged_in_{user}'):
        return render_template('login_user.html', user=user)
    
    else:
        return redirect(url_for('bp_login_form.login'))



@bp_login.route('/logout', methods=["GET", "POST"])
@bp_login.route('/logout/', methods=["GET", "POST"])
def logout():
    
    if request.method == "POST":
        
        user = request.form['user']
        session[f'logged_in_{user}'] = False
        session.pop(f'logged_in_{user}', None)
        flash('Wylogowano')
        

    return redirect(url_for('bp_index_form.index'))
    

class Login(FlaskForm):
    
    email = StringField('Podaj adres e-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Podaj hasło: ', validators=[DataRequired()])
    submit = SubmitField('Logowanie')