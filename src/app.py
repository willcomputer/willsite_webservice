from flask import Flask, jsonify, request, make_response, send_file
from flask_cors import CORS
from gpiozero import CPUTemperature
import psutil, os, json, bcrypt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
custom_salt = b"$2b$12$Rtp8g8Y1mE1mE1mE1mE1mu"

######################################################################
### User Authentication Endpoints
######################################################################

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if (not(doesUserExist)):
        return add_cors_headers(invalidUsernameRepsonse())
    
    if (not(isPasswordCorrect)):
        return add_cors_headers(badPasswordRepsonse()) 
    
    return add_cors_headers(make_response(jsonify({"session": generateSessionToken(username)}), 200))
    

@app.route('/signup', methods=['GET'])
def signup():
    username = request.args.get('username')
    password = request.args.get('password')
    
    if (doesUserExist):
        return add_cors_headers(takenUsernameRepsonse())
    
    createNewUser(username, password)
    createNewUserInStats(username)
    
    return add_cors_headers(make_response(jsonify({"session": generateSessionToken(username)}), 200))
 
    
######################################################################
### Modify stored data 
######################################################################
    
def createNewUserInAccounts(username, password): 
    path = "static/accounts.json"
    account_map = {}
    with open(path, "w") as f1:
        account_map = json.loads(f.read())
        f1.close()        
    
    account_map[username] = bcrypt.hashpw(password, custom_salt)

    with open(path, "w") as f2:
        json.dump(account_map, f2, indent=4)
        f2.close()
        
        
def createNewUserInStats(username):
    path = "static/stats.json"
    stats_map = {}
    with open(path, "w") as f1:
        stats_map = json.loads(f.read())
        f1.close()        
    
    stats_map[username] = {"spins": 0, "points": 0}

    with open(path, "w") as f2:
        json.dump(stats_map, f2, indent=4)
        f2.close()
        
        
def generateSessionToken(username):
    return "fake_session_token_please_fix_me"
        
        
######################################################################
### Verifications 
######################################################################

def validationSessionToken(username: str, token: str):
    return True

def isPasswordCorrect(username:str, password: str) -> bool:
    hashed_input = bcrypt.hashpw(password, custom_salt)
    match = False
    with open('static/accounts.json') as f:
        account_map = json.loads(f.read())
        if username in account_map:
            match = account_map[username] == hashed_input
        f.close()
    return match

def doesUserExist(username: str) -> bool:
    exists = False;
    with open('static/accounts.json') as f:
        account_map = json.loads(f.read())
        exists = username in account_map
        f.close()
    return exists

def getUserStats(username: str): 
    user_stats = {}
    with open('static/stats.json') as f:
        stats_map = json.loads(f.read())
        if username in stats_map: 
            user_stats = stats_map[username]
        f.close()
    return user_stats
     
######################################################################
### Game Logic
######################################################################


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

