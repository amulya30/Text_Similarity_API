from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)

#Connecting to default mongo port
client = MongoClient("mongodb://db:27017")

#Creating new db
db = client.SimilarDatabase

#Creating Collection
users = db["Users"]

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

#For Registering New User
class Register(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"] 

        if UserExist(username):
            retJson = {
                'status':301,
                'msg': 'Invalid Username'
            }
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #Storing username and pswd into the database
        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens":6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }
        return jsonify(retJson)

def verifyPw(username, password):
    if not UserExist(username):
        return False

    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username":username
    })[0]["Tokens"]
    return tokens

#Detecting Registered User & Allowing Text Comparison 
class Detect(Resource):
    def post(self):
        
        postedData = request.get_json()
        
        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        if not UserExist(username):
            retJson = {
                'status':301,
                'msg': "Invalid Username"
            }
            return jsonify(retJson)

        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status":302,
                "msg": "Incorrect Password"
            }
            return jsonify(retJson)
        
        #Checking user existing tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 303,
                "msg": "You are out of tokens, please refill!"
            }
            return jsonify(retJson)

        #Calculate edit distance between text1, text2
        nlp = spacy.load('es_core_news_sm')
        text1 = nlp(text1)
        text2 = nlp(text2)

        ratio = text1.similarity(text2)

        retJson = {
            "status":200,
            "ratio": ratio,
            "msg":"Similarity score calculated successfully"
        }

        #Take away 1 token from user
        current_tokens = countTokens(username)
        users.update({
            "Username":username
        }, {
            "$set":{
                "Tokens":current_tokens-1
                }
        })

        return jsonify(retJson)

#Refilling User Token
class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"]

        if not UserExist(username):
            retJson = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(retJson)

        correct_pw = "abc123"
        if not password == correct_pw:
            retJson = {
                "status":304,
                "msg": "Invalid Admin Password"
            }
            return jsonify(retJson)

        #Updating user tokens in db
        users.update({
            "Username":username
        }, {
            "$set":{
                "Tokens":refill_amount
                }
        })

        retJson = {
            "status":200,
            "msg": "Refilled successfully"
        }
        return jsonify(retJson)


api.add_resource(Register, '/register')
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')


if __name__=="__main__":
    app.run(host='0.0.0.0')


