import os
from twilio.rest import Client
from flask import Flask, request, render_template, redirect, session, url_for
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)
app.secret_key = 'verificationworks'
app.config.from_object('settings')

client = Client(
    app.config['TWILIO_ACCOUNT_SID'],
    app.config['TWILIO_AUTH_TOKEN'])

VERIFY_SERVICE_SID = app.config['VERIFY_SERVICE_SID']
MODERATOR = app.config['MODERATOR']
KNOWN_PARTICIPANTS = app.config['KNOWN_PARTICIPANTS']

def check_verification_token(phone, token):
    check = client.verify \
        .services(VERIFY_SERVICE_SID) \
        .verification_checks \
        .create(to=phone, code=token)    
    return check.status == 'approved'

@app.route("/", methods=['GET'])
def homepage():
    return("hello")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in KNOWN_PARTICIPANTS and password == KNOWN_PARTICIPANTS.get(username):
            session['username'] = username
            print("[INFO] : login successs going to verify now ")
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
    # print("[INFO] : phone number was entered. create verification token here ")
    verification = client.verify \
        .services(VERIFY_SERVICE_SID) \
        .verifications \
        .create(to=session['phonenumber'], channel='sms')
    # print("[INFO] : verification sent ")
    if request.method == 'POST':
        verificationcode = request.form['verificationcode']
        if check_verification_token(phonenumber, verificationcode):
            return render_template('success.html')
        else:
            error = "Invalid verification code. Please try again."
            return render_template('verifypage.html', error = error)
    return render_template('verifypage.html', username = username, showVerificationCode = showVerificationCode)