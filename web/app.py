from flask import Flask,jsonify,request
from flask_restful import Api,Resource
from pymongo import MongoClient
import bcrypt 

app=Flask(__name__)
api=Api(app)
#Connecting to default mongo port
client=MongoClient("mongodb://db:27017")

#creating new db
db=client.SimilarDatabase

#creating collection
users=db["Users"]

def UserExist(username):
    if users.find({"Username":username}).count() == 0:
        return False
    else:
        return True

class Register(Resource):
    def post(self):
        postedData=request.get_json()
        Username=postedData["username"]
        password=postedData["password"]
        
        if UserExist(username):
            retJson={
                "status":301,
                "msg":"Invalid Usrname"
            }
            return jsonify(retJson)
        
        hashed_pw=bcrypt.hashpw(password.encode('utf8'),brcypt.gensalt())

        users.insert({
            "Username":username,
            "Password":hashed_pw,
            "Tokens":6
        })

        retJson={
            "status":"200",
            "msg":"You've successfully signed up !"
        }

        return jsonify(retJson)
        
