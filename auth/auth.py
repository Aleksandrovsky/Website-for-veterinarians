from flask import Flask, Blueprint, render_template, url_for, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from werkzeug.security import generate_password_hash, check_password_hash

from db.db import add_data

import os

import random

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



#INITIALIZE

bp_auth = Blueprint('bp_auth_form', __name__, template_folder='templates')

db_path = (os.getcwd() + '/db_folder/database.db')

table_name = 'users'

smtp_adress = 'smtp.poczta.onet.pl'
port = 465
login = '#'
password = '#'



#ROUTES

@bp_auth.route('/login')
def login():
    return render_template('login.html')




@bp_auth.route('/registration', methods=["GET", "POST"])
def registration():
    
    form = Registration()
    
    if form.validate_on_submit():
        
        data_dict = {}
        
        email = form.email.data
        username = form.username.data
        password = form.password.data
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        if check_password_hash(hash_password, password):
            
            data_dict['email'] = email
            data_dict['username'] = username
            data_dict['hash_password'] = hash_password
            data_dict['admin'] = 0

            session['data_dict'] = data_dict
        else: 
            raise ValueError('Hash password not match with password')
        
        """ TRZEBA ZROBIĆ SPRAWDZENIE CZY DANY UŻYTKOWNIK ISTNIEJE W DB """
        """ TRZEBA ZROBIĆ AUTENTYKACJĘ MEJLEM """
        
        
        return redirect(url_for('bp_auth_form.check_code', username=username))   
     
    return render_template('registration.html', form=form)



@bp_auth.route('/registration/check_code/<username>', methods=["GET", "POST"])
def check_code(username):
    
    form_check = CheckCode()
    
    data_dict = session['data_dict']
    
    recipent_email = data_dict['email']
    
    auth_code = generate_auth_code()
    send_auth_code(auth_code, recipent_email)
    
    if form_check.validate_on_submit():
        code = form_check.code.data
        
        if code == auth_code:
            
            add_data(data_dict, table_name, db_path)
            return redirect(url_for('bp_auth_form.reg_ok'))

    return render_template('check_code.html', form_check = form_check)



@bp_auth.route('/registration/ok')
def reg_ok():
    return render_template('reg_ok.html')



#FUNCTIONS

def generate_auth_code():
    
    auth_code = []
    
    for i in range(6):

        i = random.randint(0,9)
        auth_code.append(i)
    
    auth_code = [''.join(str(i) for i in auth_code)][0]

    return auth_code



def send_auth_code(auth_code, recipent_email):
    
    message_to_recipent = "Twój kod aktywacyjny: " + str(auth_code)

    message_to_send = MIMEMultipart('alternative')
    message_to_send['Subject'] = 'Veterinarians- authentication code.'
    message_to_send['From'] = 'kretexus@onet.pl'
    message_to_send['To'] = recipent_email
    message_to_send.attach(MIMEText(message_to_recipent))

    smtp_object = smtplib.SMTP_SSL(smtp_adress, port)
    code, msg = smtp_object.ehlo()

    if code == 250:
        login_code, login_msg = smtp_object.login(login, password)
        print('Connection ok.')

        if login_code == 235:
            smtp_object.sendmail('kretexus@onet.pl', recipent_email, message_to_send.as_string())
            smtp_object.quit()
            print('Auth code send.')

        else:
            print('Didn`t send! Code: ', login_code, 'Message: ', login_msg)

    else:
        print('Didn`t connect! Code: ', code, 'Message: ', msg)



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
    
# if __name__ == '__main__':
    
#     print(generate_auth_code())