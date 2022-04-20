from functools import wraps
from flask import session,request,abort,redirect
import base64
import time
from markupsafe import re
import random
tokens = ["abc"]
password_list = {"tarang":"sgp"}
import sqlite3
con = sqlite3.connect('dockat.db',check_same_thread=False) 

cur = con.cursor()
def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username"  in session:
            time.sleep(random.choice([3, 4, 5, 6,7,8])*0.05)
            try:
               userst = list(cur.execute("Select username from login;"))
            except:
                time.sleep(0.15)
                userst = list(cur.execute("Select username from login;"))
            users = []
            for usera in userst:
                users.append(list(usera)[0]) 
            if(session["username"] not in users):
                print(users)
                abort(401)
            else:
                username = session["username"]
        elif "Authorization" in request.headers:
            if request.headers.get("Authorization")[:5:] == "Basic":
                try:
                    cred_string =  base64.b64decode(request.headers.get("Authorization")[6::])
                except:
                    abort(401)
                requested_username = str(cred_string).split(":",1)[0][2::]
                requested_password = str(cred_string).split(":",1)[1][:-1:]
                if requested_username not in users:
                    abort(401)
                if password_list[requested_username] != requested_password:
                    abort(401)
                username = requested_username    
            elif request.headers.get("Authorization")[:5:] == "Token":
                provided_token =  (request.headers.get("Authorization")[6::])  
                tokenas = list(cur.execute("select token from tokens;"))
                tokens = []
                for tok in tokenas:
                    tokens.append(list(tok)[0])
                if provided_token in tokens:
                    username = list(list(cur.execute("select username from login where user_id=(select user_id from tokens where token='%s');" %(provided_token)))[0])[0]
                else:
                    abort(401)

            else:
                abort(401)
        else:
            return redirect("/login")
                
        return f(username,*args, **kwargs)
    return decorated_function
