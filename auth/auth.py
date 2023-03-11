from flask import Flask, Blueprint, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, IntegerField

from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3

import os

from db.db import add_data



#INITIALIZE

bp_auth = Blueprint('bp_auth_form', __name__, template_folder='templates')

db_path = (os.getcwd() + '/db_folder/database.db')

generated_code = None


#ROUTES

@bp_auth.route('/login')
def login():
    return render_template('login.html')




@bp_auth.route('/registration', methods=['GET', 'POST'])
def registration():
    
    form = Registration()
    
    if form.validate_on_submit():
        
        data_dict = {}
        table_name = 'users'
        
        email = form.email.data
        username = form.username.data
        password = form.password.data
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        if check_password_hash(hash_password, password):
            
            data_dict['email'] = email
            data_dict['username'] = username
            data_dict['hash_password'] = hash_password
            data_dict['admin'] = 0
            
            add_data(data_dict, table_name, db_path)
        
        else: 
            raise ValueError('Hash password not match with password')
        
        """ TRZEBA ZROBIĆ SPRAWDZENIE CZY DANY UŻYTKOWNIK ISTNIEJE W DB """
        """ TRZEBA ZROBIĆ AUTENTYKACJĘ MEJLEM """
        
        
        return redirect(url_for('bp_auth_form.check_code'))   
     
    return render_template('registration.html', form=form)



@bp_auth.route('/registration/ok')
def reg_ok():
    return render_template('reg_ok.html')



@bp_auth.route('/registration/check_code')
def check_code():
    
    form_check = CheckCode()
    
    if form_check.validate_on_submit():
        code = form_check.code.data
        
        if code == generated_code:
            return redirect(url_for('bp_auth_form.check_code'))

            
    return render_template('check_code.html', form_check = form_check)



#CLASSES

class Registration(FlaskForm):

    email = StringField('E-mail:', validators=[DataRequired(), Email(), Length(1,80)])
    username = StringField('Nazwa użytkownika:', validators=[DataRequired(),
                Length(1,16), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Nazwa użytkownika może składać się z liter, cyfr, kropek i znaków podkreślenia')])
    password = PasswordField('Hasło:', validators=[DataRequired(), EqualTo('password_2', message='Podane hasła muszą być takie same')])
    password_2 = PasswordField('Powtórz hasło:', validators=[DataRequired()])
    submit = SubmitField('Zarejestruj się')
    
    
    
class CheckCode(FlaskForm):
    
    code = IntegerField('Wpisz kod, który wysłaliśmy na adres e-mail podany w formularzu', validators=[DataRequired(), Length(6)])
    submit =  SubmitField('Wyślij')