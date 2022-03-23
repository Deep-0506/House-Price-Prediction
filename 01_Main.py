import pandas as pd
import pickle
import json
import math
from flask import Flask , render_template , request
from flask_mail import Mail

with open('02_config.json' , "r") as d:
    parameters = json.load(d)["parameters"]

application = Flask(__name__)

application.config.update(

    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = parameters["gmail_username"],
    MAIL_PASSWORD = parameters["gmail_password"]
)

mail = Mail(application)
   
Data = pd.read_csv('Cleaned_Data.csv')
pipe = pickle.load(open("RidgeModel.pkl",'rb'))

@application.route("/")
def index():

    City = sorted(Data['City'].unique())
    BHK = sorted(Data['BHK'].unique())
    return render_template("index.html" , City = City , BHK = BHK)

@application.route("/predict" , methods = ['POST'])
def predict():

    City = request.form.get("city")
    BHK = request.form.get("bhk")
    sqft = request.form.get("sqft")

    flag = True
    Error_message = ""

    if(City == ""):

        flag = False
        Error_message += "Please Select the City \n"
    
    if(BHK == ""):

        flag = False
        Error_message += "Please Select the BHK \n"

    if(sqft == ""):

        flag = False
        Error_message += "Please Enter the Square feet value"

    if(flag == False):

        return Error_message
    else:

        inp = pd.DataFrame([[BHK , sqft , 1 , City]],columns=['BHK' , 'SQUARE_FT' , 'READY_TO_MOVE' , 'City'])
        price = pipe.predict(inp)[0]

        return ("Price : ₹ "+format(math.trunc(price))+" Lacs")

@application.route("/contact" , methods = ['POST'])
def contact():

    if(request.method == 'POST'):

        Name = request.form.get("name")
        Email = request.form.get("email")
        Contact_Number = request.form.get("cn")
        Message = request.form.get("message")

        City = sorted(Data['City'].unique())
        BHK = sorted(Data['BHK'].unique())
        
        flag = True
        Error = "Enter the "
        print(Name , Email , Contact_Number , Message)

        if(Name == ""):

            Error += " Name "
            flag = False

        if(Email == ""):

            Error += " Email "
            flag = False
        
        if(Contact_Number == ""):

            Error += " Contact Number "
            flag = False

        if(Message == "" or Message == " "):

            Error += " Message "
            flag = False
       

        if(flag == False):

            # return render_template("index.html" , response_message = Error , City = City , BHK = BHK)
            return Error
        elif(flag == True):

            mail.send_message('Mail from house prediction from '+Name+' with email '+Email,
                                sender = parameters['gmail_username'], 
                                recipients = [parameters['receiver']], 
                                body= Message)

            # return render_template("index.html" , response_message = "Mail send" ,  City = City , BHK = BHK)
            return "Mail send"

if __name__ == "__main__":

    application.run(debug = True , port=5001)