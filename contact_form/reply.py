from flask import render_template, Blueprint, url_for, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

from dotenv import load_dotenv


load_dotenv()

bp_reply = Blueprint('bp_reply_form', __name__, template_folder='templates')

smtp_adress = 'smtp.poczta.onet.pl'
port = 465
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')




@bp_reply.route('/reply', methods=['GET', 'POST'])
def reply():

    reply_email = ReplyEmail()

    if reply_email.validate_on_submit():
        
        email = request.args.get('email')
        msg = request.args.get('msg')
        message = reply_email.message.data

        print('Treść moja do klienta: ' + message + ' Od: ' + email + ' MSG od klienta: ' + msg)
        send_email(message, email, msg)

        return redirect(url_for('bp_contact_form.messages'))

    return render_template('reply.html', reply_email = reply_email)




def send_email(email, recipent_email, client_msg):

    email_to_send = str(email)
    client_msg = str(client_msg)
    
    html_msg = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
        </head>
        <body>
            <p>Witaj!</p>
            <p>Odpowiadam na Twoją wiadomość:</p>
            <p>"{client_msg}"</p>
            <br>
            <p>{email_to_send}</p>
        </body>
        </html>
    """

    message_to_send = MIMEMultipart('alternative')
    message_to_send['Subject'] = 'Message from Aleksander'
    message_to_send['From'] = 'kretexus@onet.pl'
    message_to_send['To'] = recipent_email
    message_to_send.attach(MIMEText(html_msg))

    smtp_object = smtplib.SMTP_SSL(smtp_adress, port)
    code, msg = smtp_object.ehlo()

    if code == 250:
        login_code, login_msg = smtp_object.login(login, password)
        print('Connection ok.')

        if login_code == 235:
            smtp_object.sendmail('kretexus@onet.pl', recipent_email, message_to_send.as_string())
            smtp_object.quit()
            print('Message send.')

        else:
            print('Didn`t send! Code: ', login_code, 'Message: ', login_msg)

    else:
        print('Didn`t connect! Code: ', code, 'Message: ', msg)




class ReplyEmail(FlaskForm):

    message = StringField('Message: ', validators = [DataRequired()])
    submit = SubmitField('Send message')