from flask import Flask, jsonify, request, make_response, send_file
from flask_cors import CORS
# from gpiozero import CPUTemperature
import psutil, os, json, bcrypt, random, string, time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
custom_salt = b"$2b$12$Rtp8g8Y1mE1mE1mE1mE1mu"
characters = string.ascii_letters + string.digits


######################################################################
### Web service health check
######################################################################

@app.route('/', methods=['GET'])
def healthcheck():
    return add_cors_headers(jsonify({"status": True}))
     
######################################################################
### User Authentication Endpoints
######################################################################

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password').encode('utf-8')

    if not(doesUserExist(username)):
        return add_cors_headers(invalidUsernameRepsonse())
    
    if not(isPasswordCorrect(username, password)):
        return add_cors_headers(badPasswordRepsonse()) 

    session_token = generateSessionToken()

    updateSessionToken(username, session_token)
    
    return add_cors_headers(make_response(jsonify({"session": session_token}), 200))
    

@app.route('/signup', methods=['GET'])
def signup():
    username = request.args.get('username')
    password = request.args.get('password').encode('utf-8')
    
    if doesUserExist(username):
        return add_cors_headers(takenUsernameRepsonse())
    
    session_token = createNewUserInAccounts(username, password)
    createNewUserInStats(username)
    
    return add_cors_headers(make_response(jsonify({"session": session_token}), 200))
 
    
######################################################################
### Modify stored data 
######################################################################
    
def createNewUserInAccounts(username, password): 
    path = "static/accounts.json"
    account_map = {}
    with open(path, "r") as f1:
        account_map = json.loads(f1.read())
        f1.close()        
    
    hashed_password = bcrypt.hashpw(password, custom_salt).decode('utf-8')
    session_token = generateSessionToken()

    account_map[username] = {'password': hashed_password, 'token': session_token, 'last_roll': 0}

    with open(path, "w") as f2:
        json.dump(account_map, f2, indent=4)
        f2.close()
    
    return session_token
        
        
def createNewUserInStats(username):
    path = "static/stats.json"
    stats_map = {}
    with open(path, "r") as f1:
        stats_map = json.loads(f1.read())
        f1.close()        
    
    stats_map[username] = {"spins": 0, "points": 0}

    with open(path, "w") as f2:
        json.dump(stats_map, f2, indent=4)
        f2.close()
        
        
def generateSessionToken():
    return ''.join(random.choices(characters, k=15))


def updateSessionToken(username, session_token):
    path = "static/accounts.json"
    account_map = {}
    with open(path, "r") as f1:
        account_map = json.loads(f1.read())
        f1.close()        
    
    account_map[username]['token'] = session_token

    with open(path, "w") as f2:
        json.dump(account_map, f2, indent=4)
        f2.close()

def updateRollWindow(username, time):
    path = "static/accounts.json"
    account_map = {}
    with open(path, "r") as f1:
        account_map = json.loads(f1.read())
        f1.close()        
    
    account_map[username]['last_roll'] = time

    with open(path, "w") as f2:
        json.dump(account_map, f2, indent=4)
        f2.close()


def updateUserStats(username, score):
    path = "static/stats.json"
    stats_map = {}
    with open(path, "r") as f1:
        stats_map = json.loads(f1.read())
        f1.close()        
    
    stats_map[username]['points'] = stats_map[username]['points'] + score
    stats_map[username]['spins'] = stats_map[username]['spins'] + 1


    with open(path, "w") as f2:
        json.dump(stats_map, f2, indent=4)
        f2.close()
        
        
######################################################################
### Verifications 
######################################################################

def validationSessionToken(username, token):
    return True

def isPasswordCorrect(username, password) -> bool:
    hashed_input = bcrypt.hashpw(password, custom_salt).decode('utf-8')
    match = False
    with open('static/accounts.json') as f:
        account_map = json.loads(f.read())
        if username in account_map:
            match = account_map[username]['password'] == hashed_input
        f.close()
    return match

def doesUserExist(username) -> bool:
    exists = False
    with open('static/accounts.json') as f:
        account_map = json.loads(f.read())
        exists = username in account_map
        f.close()
    return exists

def isRollWindowOpen(username, time) -> bool:
    return True



     
######################################################################
### Game Logic
######################################################################

symbols = ['cherry', 'bar', 'seven', 'bell']
weights = [25, 15, 10, 50]


@app.route('/roll', methods=['GET'])
def roll():
    username = request.args.get('username')
    session_token = request.args.get('token')
    time = request.args.get('time')

    if not(doesUserExist(username)):
        return add_cors_headers(invalidUsernameRepsonse())

    if not(validationSessionToken(username, session_token)):   
        return add_cors_headers(invalidSessionToken())

    if not(isRollWindowOpen(username, time)):
        return add_cors_headers(tooFastRoll())

    updateRollWindow(username, time)

    results = random.choices(symbols, weights=weights, k=3)

    score = calculateScore(results)

    updateUserStats(username, score)

    return add_cors_headers(packageRollResponse(results))


def calculateScore(results):
    return 10



@app.route('/stats', methods=['GET'])
def stats():
    username = request.args.get('username')

    if not(doesUserExist(username)):
        return add_cors_headers(invalidUsernameRepsonse())

    return add_cors_headers(packageStats(getUserStats(username)))


def getUserStats(username): 
    user_stats = {}
    with open('static/stats.json') as f:
        stats_map = json.loads(f.read())
        if username in stats_map: 
            user_stats = stats_map[username]
        f.close()
    return user_stats
    
    

# create the following methods
# 1. roll(username, sessionToken) - rolls the slot and returns the ending slot state and updated player stats
# 2. fetchStats(username) - indepth stats for player 


######################################################################
### Pi Health Check
######################################################################

@app.route('/pi-health', methods=['GET'])
def pi_health():
    temp = CPUTemperature().temperature
    cpu_load = psutil.cpu_percent()
    percent_used_memory = psutil.virtual_memory().percent
    response = jsonify(temperature=temp, cpuLoadPercentage=cpu_load, percentUsedMemory=percent_used_memory)
    return add_cors_headers(response)

######################################################################
### Responses 
######################################################################

def packageStats(stats):
    return make_response(jsonify(stats), 200)

def packageRollResponse(roll_results):
    return make_response(jsonify(roll_results), 200)

def tooFastRoll():
    return make_response(jsonify({"message": "Woah! Slow down! Wait at least 5 seconds between each spin"}), 404)

def invalidSessionToken():
    return make_response(jsonify({"message": "Invalid Session Token. Please relogin"}), 404)

def takenUsernameRepsonse():
    return make_response(jsonify({"message": "Username already exists"}), 404)

def invalidUsernameRepsonse():
    return make_response(jsonify({"message": "Username does not exist"}), 404)

def badPasswordRepsonse():
    return make_response(jsonify({"message": "Invalid Password"}), 404)
    
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "GET, POST")
    response.headers.add("Access-Control-Allow-Methods", "Content-Type") 
    return response


######################################################################
### Python shit
######################################################################
if __name__ == '__main__':
    app.run()

