import os
from twilio.rest import Client
from flask import Flask, request, render_template, redirect, session, url_for
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)
app.secret_key = 'combinedroute'
app.config.from_object('settings')

client = Client(
    app.config['TWILIO_ACCOUNT_SID'],
    app.config['TWILIO_AUTH_TOKEN'])

VERIFY_SERVICE_SID = app.config['VERIFY_SERVICE_SID']
MODERATOR = app.config['MODERATOR']
KNOWN_PARTICIPANTS = app.config['KNOWN_PARTICIPANTS']

@app.route("/", methods=['GET'])
def homepage():
    print("[INFO] : KNOWN_PARTICIPANTS = ", KNOWN_PARTICIPANTS)
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
        print("[INFO] : inside enter phone number now ")
        phonenumber = request.form['phonenumber']
        session['phonenumber'] = phonenumber    
        print("[INFO] : session['phonenumber'] = ", phonenumber)
        if phonenumber: 
            return redirect(url_for('generate_verification_code'))
        else:
            error = "Enter valid phone number."
            return render_template('verifypage.html', error = error)
    return render_template('verifypage.html', username = username, phoneNumberEmpty = phoneNumberEmpty)

@app.route('/verifyme', methods=['GET', 'POST'])
def generate_verification_code():
    username = session['username']
    showVerificationCode = True
    print("[INFO] : phone number was entered. create verification token here ")
    verification = client.verify \
                        .services('VXXXXXX') \
                        .verifications \
                        .create(to=session['phonenumber'], channel='sms')
    print("[INFO] : verification sent ")
    return render_template('verifypage.html', username = username, showVerificationCode = showVerificationCode)
