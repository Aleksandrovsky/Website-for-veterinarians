from flask import Blueprint, render_template, url_for, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from werkzeug.security import generate_password_hash, check_password_hash

from db.db import add_data, get_data

import os

import random

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv



#INITIALIZATION
load_dotenv()

bp_auth = Blueprint('bp_auth_form', __name__, template_folder='templates')

db_path = (os.getcwd() + '/db_folder/' + str(os.getenv('DB_NAME')))

table_name = 'users'
all_auth_codes = []

smtp_adress = 'smtp.poczta.onet.pl'
port = 465
email_login = os.getenv('LOGIN')
email_password = os.getenv('PASSWORD')



#ROUTES
@bp_auth.route('/registration', methods=["GET", "POST"])
@bp_auth.route('/registration/', methods=["GET", "POST"])
def registration():
    
    form = Registration()
    
    if form.validate_on_submit():
        
        data_dict = {}
        
        email = form.email.data
        username = form.username.data
        password = form.password.data
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            
        db_values = ['email', 'username']
        db_query = get_data(db_values, db_path, table_name)
        
        registered = False

        if len(db_query) < 1:
            
            print('Zapytanie IF: ', db_query)
            
            if check_password_hash(hash_password, password):
                        
                data_dict['email'] = email
                data_dict['username'] = username
                data_dict['hash_password'] = hash_password
                data_dict['admin'] = 0

                auth_code = generate_auth_code()
                all_auth_codes.append(auth_code)
                print('Pusta baza danych')
                print(all_auth_codes)
                        
                session[f'data_dict_{username}'] = data_dict
                session[f'auth_code_{username}'] = auth_code
                        
                send_auth_code(auth_code, email)
                
                flash('Na podany adres e-mail wysłaliśmy kod autoryzacyjny!')
                    
                return redirect(url_for('bp_auth_form.check_code', username=username))  
            
            else: 
                
                raise ValueError('Hash password not match with password')
                     
        else:
            
            while registered == False:
                
                for e, u in db_query:
                    
                    if (e == email) or (u == username):
                        
                        if (e == email):
                            flash('Istnieje już konto o podanym adresie e-mail!')
                            return redirect(url_for('bp_auth_form.registration'))
                        
                        else:
                            flash('Nazwa użytkownika jest zajęta!')
                            return redirect(url_for('bp_auth_form.registration'))
                        
                if check_password_hash(hash_password, password):
                    
                    data_dict['email'] = email
                    data_dict['username'] = username
                    data_dict['hash_password'] = hash_password
                    data_dict['admin'] = 0

                    auth_code = generate_auth_code()
                    all_auth_codes.append(auth_code)
                    
                    session[f'data_dict_{username}'] = data_dict
                    session[f'auth_code_{username}'] = auth_code
                    
                    send_auth_code(auth_code, email)
                    
                    registered = True
                    
                    flash('Na podany adres e-mail wysłaliśmy kod autoryzacyjny!')
            
                    return redirect(url_for('bp_auth_form.check_code', username=username))  
                
                else: 
                    raise ValueError('Hash password not match with password')
                        
    
    return render_template('registration.html', form=form)



@bp_auth.route('/registration/check_code/<username>', methods=["GET", "POST"])
@bp_auth.route('/registration/check_code/<username>/', methods=["GET", "POST"])
def check_code(username):
    
    form_check = CheckCode()
    
    data_dict = session[f'data_dict_{username}']
    auth_code = session[f'auth_code_{username}']
    
    if form_check.validate_on_submit():
        
        code = form_check.code.data
        
        if code == auth_code:
            
            add_data(data_dict, table_name, db_path)
            print('Użytkownik dodany')
            
            return redirect(url_for('bp_auth_form.registration_ok', username=username))
        
        else:
            print('Kod aktywacyjny niepoprawny!')

    return render_template('check_code.html', form_check = form_check)



@bp_auth.route('/registration/<username>/done')
@bp_auth.route('/registration/<username>/done/')
def registration_ok(username):
    
    session.pop(f'data_dict_{username}', None)
    
    auth_code = session[f'auth_code_{username}']
    all_auth_codes.remove(auth_code)
    print('Lista wszystkich kodów:', all_auth_codes)
    
    session.pop(f'auth_code_{username}', None)
    
    return render_template('registration_ok.html')


@bp_auth.route('/registration/problem', methods=["GET", "POST"])
@bp_auth.route('/registration/problem/', methods=["GET", "POST"])
def reg_no_ok():
    
    problem_info = session['problem']
    
    return render_template('reg_no_ok.html', problem_info=problem_info)


#IT`S ONLY FOR TEST
@bp_auth.route('/wyczysc')
def czysc():
    session.clear()
    return '<p>Wyczysczone</p>'



#FUNCTIONS
def generate_auth_code():
    
    auth_code = []
    is_ok = False
    
    while is_ok == False:
    
        for i in range(6):

            i = random.randint(0,9)
            auth_code.append(i)
        
        if auth_code in all_auth_codes:
            auth_code = []
            print('Kod istnieje, wygeneruj jeszcze raz.')
            
        else:    
            auth_code = [''.join(str(i) for i in auth_code)][0]
            is_ok = True
            print('Kod nie istnieje, wyślij kod do autoryzacji.')

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
        login_code, login_msg = smtp_object.login(email_login, email_password)
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
    
    code = StringField('Wpisz kod, który wysłaliśmy na adres e-mail podany w formularzu', validators=[DataRequired()])
    submit =  SubmitField('Wyślij')