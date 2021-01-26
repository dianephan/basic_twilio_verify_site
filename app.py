import os
from dotenv import load_dotenv
from twilio.rest import Client
from flask import Flask, request, render_template, redirect, session, url_for
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

load_dotenv()
app = Flask(__name__)
app.secret_key = 'secretkeyfordungeonxxx'
app.config.from_object('settings')

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN= os.environ.get('TWILIO_AUTH_TOKEN')
VERIFY_SERVICE_SID= os.environ.get('VERIFY_SERVICE_SID')

client = Client()

KNOWN_PARTICIPANTS = app.config['KNOWN_PARTICIPANTS']

def check_verification_token(phone, token):
    check = client.verify \
        .services(VERIFY_SERVICE_SID) \
        .verification_checks \
        .create(to=phone, code=token)    
    return check.status == 'approved'

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in KNOWN_PARTICIPANTS and password == KNOWN_PARTICIPANTS.get(username):
            session['username'] = username
            return redirect(url_for('enter_phonenumber'))
        error = "Invalid login credentials. Please try again."
        return render_template('index.html', error = error)
    return render_template('index.html')

@app.route('/enterphone', methods=['GET', 'POST'])
def enter_phonenumber():
    phoneNumberEmpty = True
    username = session['username']
    if request.method == 'POST':
        phonenumber = request.form['phonenumber']
        session['phonenumber'] = phonenumber    
        if phonenumber: 
            return redirect(url_for('generate_verification_code'))
        else:
            error = "Enter valid phone number."
            return render_template('verifypage.html', error = error)
    return render_template('verifypage.html', username = username, phoneNumberEmpty = phoneNumberEmpty)

@app.route('/verifyme', methods=['GET', 'POST'])
def generate_verification_code():
    username = session['username']
    phonenumber = session['phonenumber']    
    error = None
    showVerificationCode = True
    verification = client.verify \
        .services(VERIFY_SERVICE_SID) \
        .verifications \
        .create(to=session['phonenumber'], channel='sms')
    if request.method == 'POST':
        verificationCode = request.form['verificationcode']
        if check_verification_token(phonenumber, verificationCode):
            return render_template('success.html', username = username)
        else:
            error = "Invalid verification code. Please try again."
            return render_template('verifypage.html', error = error, showVerificationCode = showVerificationCode)
    return render_template('verifypage.html', username = username, showVerificationCode = showVerificationCode)