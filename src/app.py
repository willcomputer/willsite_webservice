from flask import Flask, jsonify, request, make_response, send_file
from flask_cors import CORS
from gpiozero import CPUTemperature
import psutil, os, json, smtplib, email, csv, configparser
import json

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

blog_password='police'
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/pi-health', methods=['GET'])
def pi_health():
    temp = CPUTemperature().temperature
    cpu_load = psutil.cpu_percent()
    percent_used_memory = psutil.virtual_memory().percent
    response = jsonify(temperature=temp, cpuLoadPercentage=cpu_load, percentUsedMemory=percent_used_memory)
    return add_cors_headers(response)

@app.route('/auth/blog', methods=['GET'])
def blog_auth():
    input = request.args.get('password')
    response = make_response()

    if input == blog_password:
        response = jsonify(result=True)
    else:
        response = jsonify(result=False)

    return add_cors_headers(response)

@app.route('/get-blogs', methods=['GET'])
def fetch_blogs():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'blogs.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)

@app.route('/get-development-blogs', methods=['GET'])
def fetch_development_blogs():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'development-blogs.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)

@app.route('/get-private-blogs', methods=['GET'])
def fetch_private_blogs():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'private-blogs.json')
    data = json.load(open(json_url))
    response = jsonify(data)
    
    print("#############################")
    print("private blogs accessed!")
    print("#############################")
    return add_cors_headers(response)

@app.route('/add-email', methods=['GET'])
def add_email_address():
    input = request.args.get('email')

    with open('email-list.csv', 'a', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([input])

    response = make_response()
    try:
        send_confirmation(input)
        response = jsonify(message=True)
        return add_cors_headers(response)
    except: 
        response = jsonify(message=False)
        return add_cors_headers(response)

@app.route('/get-bird-list', methods=['GET'])
def fetch_bird_list():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'birds.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)


@app.route('/get-bird-photo-list', methods=['GET'])
def fetch_bird_photo_id_list():

    input = request.args.get('bird-name')
    response = make_response()

    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'birds-photo-ids.json')
    data = json.load(open(json_url))
    response = jsonify(photos=data[input])

    return add_cors_headers(response)


@app.route('/get-bird-image', methods=['GET'])
def fetch_bird_image():
    input = request.args.get('image-name')  
    return send_file('static/photos/birds/' + input, mimetype='image/gif')


@app.route('/get-tamagotchi', methods=['GET'])
def fetch_tamagotchi():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'tamagotchi.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)



@app.route('/update-tamagotchi', methods=['POST'])
def update_tamagotchi():

    data = request.json
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'tamagotchi.json')

    jsonFile = open(json_url, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

    response = jsonify(message=True)
    return add_cors_headers(response)

@app.route('/feed-tamagotchi', methods=['GET'])
def feed_tamagotchi():
    
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'tamagotchi.json')

    jsonFile = open(json_url, "w+")
    jsonFile['isHungry'] = False
    jsonFile.write(json.dumps(data))
    jsonFile.close()
    response = jsonify(message=True)
    return add_cors_headers(response)

@app.route('/get-tamagotchi-sprite', methods=['GET'])
def fetch_tamagotchi_sprite():
    input = request.args.get('age')  
    with open('static/tamagotchi.json') as f:
        photo_dic = json.loads(f.read())

    return send_file('static/photos/tamagotchi/' + input + ".png", mimetype='image/gif')


@app.route('/get-rds-report', methods=['GET'])
def fetch_rds_report():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'rds.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)


@app.route('/get-book-cover', methods=['GET'])
def fetch_book_cover():
    input = request.args.get('id')  
    with open('static/book-covers.json') as f:
        photo_dic = json.loads(f.read())

    return send_file('static/photos/book-covers/' + photo_dic[input]["file"], mimetype='image/gif')

@app.route('/get-completed-books', methods=['GET'])
def fetch_completed_books():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'books-finished.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)

@app.route('/get-current-books', methods=['GET'])
def fetch_current_books():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'books-current-reading.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)

@app.route('/get-upcoming-books', methods=['GET'])
def fetch_upcoming_books():
    response = make_response()

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, 'static', 'books-upcoming.json')
    data = json.load(open(json_url))
    response = jsonify(data)

    return add_cors_headers(response)



@app.route('/get-image', methods=['GET'])
def fetch_image():
    input = request.args.get('id')  
    with open('static/photos.json') as f:
        
        photo_dic = json.loads(f.read())
        # print(photo_dic[input])

    return send_file('static/photos/' + photo_dic[input]["file"], mimetype='image/gif')

@app.route('/get-image-description', methods=['GET'])
def fetch_image_description(): 
    input = request.args.get('id')  
    with open('static/photos.json') as f:
        photo_dic = json.loads(f.read())
        # print(photo_dic[input])

    response = jsonify(description=photo_dic[input]["description"])
    return add_cors_headers(response)

def send_confirmation(input):
    real = 'thewillbucher@gmail.com'
    alias = 'will@will.computer'
    toaddy = input
    subject = 'Welcome to the Mailing List'
    body = 'Confirmed! You\'ve been added to the mailing list to receive notifications when I post new blogs.'
    bcc = []
    message = MIMEMultipart()
    message["From"] = alias
    message["To"] = toaddy
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    send_email(real, alias, toaddy, bcc, message)

@app.route('/send-update', methods=['GET'])
def send_update_email():

    real = 'thewillbucher@gmail.com'
    alias = 'will@will.computer'
    toaddy = alias
    subject = 'New Blog Alert!'
    body = 'A new blog has been posted, go check it out! https://will.computer/blog'
    bcc = []

    with open('email-list.csv', newline='\n') as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in rows:
            bcc.append(row[0])

    print("Sending to the following:")
    print(bcc)

    message = MIMEMultipart()
    message["From"] = alias
    message["To"] = toaddy
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    response = make_response()
    try:
        send_email(real, alias, toaddy, bcc, message)
        response = jsonify(message=True)
        return add_cors_headers(response)
    except: 
        response = jsonify(message=False)
        return add_cors_headers(response)


@app.route('/send-development-update', methods=['GET'])
def send_dev_update_email():

    real = 'thewillbucher@gmail.com'
    alias = 'will@will.computer'
    toaddy = alias
    subject = 'New Development Blog Alert!'
    body = 'A new development blog has been posted, go check it out! https://will.computer/development-blog'
    bcc = []

    with open('email-list.csv', newline='\n') as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in rows:
            bcc.append(row[0])

    print("Sending to the following:")
    print(bcc)

    message = MIMEMultipart()
    message["From"] = alias
    message["To"] = toaddy
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    response = make_response()
    try:
        send_email(real, alias, toaddy, bcc, message)
        response = jsonify(message=True)
        return add_cors_headers(response)
    except: 
        response = jsonify(message=False)
        return add_cors_headers(response)

@app.route('/send-private-update', methods=['GET'])
def send_private_update_email():

    real = 'thewillbucher@gmail.com'
    alias = 'will@will.computer'
    toaddy = alias
    subject = 'New Private Blog Alert!'
    
    body = 'A new private blog has been posted, the password right now is "'+ blog_password +'". Go check it out! https://will.computer/blog'
    bcc = []

    with open('private-email-list.csv', newline='\n') as csvfile:
        rows = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in rows:
            bcc.append(row[0])

    print("Sending to the following:")
    print(bcc)

    message = MIMEMultipart()
    message["From"] = alias
    message["To"] = toaddy
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    response = make_response()
    try:
        send_email(real, alias, toaddy, bcc, message)
        response = jsonify(message=True)
        return add_cors_headers(response)
    except: 
        response = jsonify(message=False)
        return add_cors_headers(response)

def send_email(real_email, alias_email, toaddy, bcc, message):
    server = 'smtp.gmail.com'
    port = 587
    pw = get_email_password()
    
    mail = smtplib.SMTP(server, port)

    mail.ehlo()
    mail.starttls()
    mail.login(real_email, pw )
    try:
        mail.sendmail(alias_email, [toaddy] + bcc, message.as_string())
        print('E-mail sent.')
    except:
        print('E-mail not sent.')

    mail.close()

def get_email_password():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.get('Email', 'password')

def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "GET, POST")
    response.headers.add("Access-Control-Allow-Methods", "Content-Type") 
    return response

if __name__ == '__main__':
    app.run()

