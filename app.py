#Chatbot Tutorial with Firebase
#Import Library
import json
import os
import gspread
from flask import Flask
from flask import request
from flask import make_response
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

#----Additional from previous file----
from random import randint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("bot1159-djtvyd-firebase-adminsdk-xb2zw-9c436fa078.json")
firebase_admin.initialize_app(cred)
#-------------------------------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet = client.open("Stackpython").worksheet('Sheet1')
# Flask
app = Flask(__name__)
@app.route('/', methods=['POST']) #Using post as a method

def MainFunction():
    #Getting intent from Dailogflow
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)

    #Call generating_answer function to classify the question
    answer_from_bot = generating_answer(question_from_dailogflow_raw)
    #-----
    
    #Make a respond back to Dailogflow
    r = make_response(answer_from_bot)
    r.headers['Content-Type'] = 'application/json' #Setting Content Type

    return r

def generating_answer(question_from_dailogflow_dict):

    #Print intent that recived from dialogflow.
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))

    #Getting intent name form intent that recived from dialogflow.
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"] 

    #Select function for answering question
    if intent_group_question_str == 'กินอะไรดี':
        answer_str = menu_recormentation()
    elif intent_group_question_str == 'Foop': 
        answer_str = crerr(question_from_dailogflow_dict)
    else: answer_str = "ผมไม่เข้าใจ คุณต้องการอะไร"

    #Build answer dict 
    answer_from_bot = {"fulfillmentText": answer_str}
    
    #Convert dict to JSON
    answer_from_bot = json.dumps(answer_from_bot, indent=4) 
    
    return answer_from_bot

def menu_recormentation(): #Function for recommending menu
    #----Additional from previous file----
    database_ref = firestore.client().document('Food/Menu_List')
    database_dict = database_ref.get().to_dict()
    database_list = list(database_dict.values())
    ran_menu = randint(0, len(database_list)-1)
    menu_name = database_list[ran_menu]
    #-------------------------------------
    answer_function = menu_name + ' สิ น่ากินนะ'
    return answer_function

def crerr(respond_dict): 

    #Getting Weight and Height
    name = respond_dict["queryResult"]["outputContexts"][1]["parameters"]["name.original"]
    lang = respond_dict["queryResult"]["outputContexts"][1]["parameters"]["L.original"]
    sheet.insert_row([name,lang],2)
    return "ลงทะเบียนเรียบร้อย"
    

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
