
from cmath import exp
from crypt import methods
from config import *
from flask import Flask,session,request,abort,redirect,send_from_directory,send_file
from functools import wraps
import os
from flask import jsonify,render_template
from backend.login_manager import login_required
import time
import random 
import string
import ast
from backend.helper import tuple_to_dict
from backend.helper import can_user_access_doc
import random
app = Flask(__name__)

from tasks import processdoc
from tasks import id_generator   
import sqlite3
con = sqlite3.connect('dockat.db',check_same_thread=False) 

cur = con.cursor()



#TODO change the secret key to something unique and random
app.secret_key = 'asdasdasd'


@app.route("/")
@login_required
def index(username):
    return render_template("dashboard.html")


@app.route("/documents")
@login_required
def documents_page(username):
    return render_template("documents.html")


#login page
@app.route("/login", methods = ["POST","GET"])
def login_page():
    if request.method == "POST":
        user_l = list(cur.execute("select username from login;"))
        password_ = list(cur.execute("select password from login;"))
        user_list = [list(l)[0] for l in user_l]
        password_l = [list(l)[0] for l in password_]
        if request.form["username"] in user_list and password_l[user_list.index(request.form["username"])] == request.form["password"]:
            session["username"] = request.form["username"]
            return redirect("/")
        else:
            print(user_list)
            return redirect("/login")
    else:
        return render_template("login.html")


@app.route("/logs")
@login_required
def renderlogs(username):
    b_lines = [row for row in (list(open("celery.logs")))]
    return render_template("logs.html",b_lines=b_lines)

@app.route('/processing')
@login_required
def processingrendererrrr(username):
    return render_template("processing.html")

@app.route("/logout")
@login_required
def logoutuser(username):
    session.clear()
    return redirect("/")


#token api

@app.route("/api/token/",methods=["GET","POST"])
def generatetoken():
    if request.method == "GET":
        
        abort(405)   
        
        
    else:
        
        li = list(cur.execute("select user_id from login where username='%s' and password='%s'" %(request.json["username"],request.json["password"])))
        if(len(li)==0):
            abort(401)
        

        token_dict = {}
        token_dict["token"] = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 40))
        r_user_id = str(list(li[0])[0])
        cur.execute("insert into tokens values ('%s',%s);" %(token_dict["token"],r_user_id));
        cur.execute("commit;")
        
        
        
        return jsonify(token_dict)


#dummy apis
@app.route("/api/")
def apicheck():
    return jsonify({"DocKat":"V0.8"})







##Documents api



@app.route("/api/documents/thumbnails/<doc_id>")
@login_required
def serverThumbnail(username,doc_id):
    time.sleep(random.choice([3, 4, 5, 6,7,8,9,10,11,12,13,14,15])*0.05)
    
       
    try:
        r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
          
    except:
        time.sleep(0.21)
        r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    access_details = can_user_access_doc(r_user_id,doc_id)
    if(access_details["not_found"]==True):
        abort(404)
    if(access_details["Read"]==False):
        abort(401)
    thumbnail_path = os.path.join(media_folder,"thumbnails",doc_id+"-thumbnail.png")
    original_name = list(list(cur.execute("select original_name from documents where doc_id='%s'"%(doc_id)))[0])[0]
    return send_file(path_or_file=thumbnail_path,download_name=original_name)



@app.route("/api/documents/download/<doc_id>")
@login_required
def servePDF(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    access_details = can_user_access_doc(r_user_id,doc_id)
    if(access_details["not_found"]==True):
        abort(404)
    if(access_details["Read"]==False):
        abort(401)
    thumbnail_path = list(list(cur.execute("select file_path from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_name = list(list(cur.execute("select original_name from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_namee = original_name.rsplit(".",1)[0] +".pdf"
    return send_file(path_or_file=thumbnail_path,download_name=original_namee,as_attachment=True)


@app.route("/api/documents/prev/<doc_id>")
@login_required
def servsePDF(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    access_details = can_user_access_doc(r_user_id,doc_id)
    if(access_details["not_found"]==True):
        abort(404)
    if(access_details["Read"]==False):
        abort(401)
    thumbnail_path = list(list(cur.execute("select file_path from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_name = list(list(cur.execute("select original_name from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_namee = original_name.rsplit(".",1)[0] +".pdf"
    
    return send_file(path_or_file=thumbnail_path,download_name=original_namee)




@app.route("/api/del/doc/<doc_id>")
@login_required
def deldoc(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    prem = can_user_access_doc(r_user_id,doc_id)
    if prem["write"]==True:
        cur.execute("delete from tags_ref where doc_id='%s';"%(doc_id))
        cur.execute("delete from documents where doc_id='%s';"%(doc_id))
        cur.execute("commit;")
    else:
        abort(403)
    return "DELETED"





@app.route("/api/documents/archive/<doc_id>")
@login_required
def servearchieve(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    access_details = can_user_access_doc(r_user_id,doc_id)
    if(access_details["not_found"]==True):
        abort(404)
    if(access_details["Read"]==False):
        abort(401)
    thumbnail_path = list(list(cur.execute("select original_path from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_name = list(list(cur.execute("select original_name from documents where doc_id='%s'"%(doc_id)))[0])[0]
    
    return send_file(path_or_file=thumbnail_path,download_name=original_name,as_attachment=True)









@app.route("/api/documents/")
@login_required
def documentsapi(username):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    document_list = tuple_to_dict(list(map(list,cur.execute("select * from documents where owner=%s or doc_id in (select doc_id from tags_ref where tag_id in (select tag_id from usertags where user_id = %s ) )"%(r_user_id,r_user_id)))))
    


    
    return jsonify({"count":len(document_list),"results":document_list})



@app.route("/api/tag/create",methods=["POST"])
@login_required
def createtag(username):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    tag_name = request.json["tag_name"]
    tag_color = request.json["tag_color"]
    cur.execute("insert into tags (tag_name,tag_color,owner) values ('%s','%s',%s);"%(tag_name,tag_color,r_user_id))
    tag_id = list(list(cur.execute("select tag_id from tags where tag_name='%s';"%(tag_name)))[0])[0]
    cur.execute("insert into usertags (tag_id,user_id,write) values (%s,%s,1);"%(tag_id,r_user_id))
    cur.execute("commit;")
    return jsonify({"tag_id":tag_id})

@app.route("/api/tag/adduser/",methods=["GET","POST"])
@login_required
def addusertag(username):
    if request.method=="GET":
        abort(404)
    elif request.method=="POST":
        r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
        tag_id = request.json["tag_id"]
        user_id = request.json["user_id"]
        write = request.json["write"]
        owner = list(list(cur.execute("select owner from tags where tag_id=%s"%(tag_id)))[0])[0]
        if(owner==r_user_id):
            if write:
                cur.execute("insert into usertags (tag_id,user_id,write) values (%s,%s,%s);"%(tag_id,user_id,1))
            else:
                cur.execute("insert into usertags (tag_id,user_id,write) values (%s,%s,%s);"%(tag_id,user_id,0))
            cur.execute("commit;")
            return "USER ADDED"
        else:
            abort(403)
                
@app.route("/api/tags/adddoc/",methods=["POST"])
@login_required
def adddoctotag(username):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    tag_id = request.json["tag_id"]
    doc_id = request.json["doc_id"]
    write = list(cur.execute("select write from usertags where tag_id=%s and user_id=%s and write=1"%(tag_id,r_user_id)))
    if(len(write)==0):
        abort(403)
    else:
        cur.execute("insert into tags_ref (tag_id,doc_id) values (%s,'%s');"%(tag_id,doc_id))
        tags=list(list(cur.execute("select tags from documents where doc_id='%s';"%(doc_id)))[0])[0]
        
        cur.execute("commit;")
        return "ADDED"

          
@app.route("/api/tag/info/<tag_id>")
@login_required
def tag_info(username,tag_id):
    x = list(list(cur.execute("select tag_color,tag_name from tags where tag_id=%s;"%(tag_id)))[0])
    return jsonify({"tag_name":x[1],"tag_color":x[0]})


@app.route("/api/documents/post_document/" ,methods=["GET","POST"])
@login_required
def uploaddoc(username):
    
    if request.method=="GET":
        abort(401)
    file = request.files['document']
    filename = file.filename
    f_id = id_generator()
    tem_path = os.path.join(temp_folder,f_id+"."+filename.split('.')[-1])
    file.save(tem_path)
    processdoc.delay(f_id,tem_path,username)
    doc_user_id = list(list(cur.execute("select user_id from login where username='%s';"%(username)))[0])[0]
    cur.execute("insert into documents values ('%s','%s',%s,%s,'%s',%s,%s,%s,%s,'%s');" %(f_id,(filename.rsplit(".",1)[0]),"NULL",str(doc_user_id),"[]","NULL","NULL","NULL","NULL",filename)) 
    cur.execute("commit;")



    return "UPLOADED"

@app.route("/api/document/post_document/" ,methods=["GET","POST"])
@login_required
def uplosaddoc(username):
    
    if request.method=="GET":
        abort(401)
    file = request.files['document']
    filename = file.filename
    f_id = id_generator()
    tem_path = os.path.join(temp_folder,f_id+"."+filename.split('.')[-1])
    file.save(tem_path)
    processdoc.delay(f_id,tem_path,username)
    doc_user_id = list(list(cur.execute("select user_id from login where username='%s';"%(username)))[0])[0]
    cur.execute("insert into documents values ('%s','%s',%s,%s,'%s',%s,%s,%s,%s,'%s');" %(f_id,(filename.rsplit(".",1)[0]),"NULL",str(doc_user_id),"[]","NULL","NULL","NULL","NULL",filename)) 
    cur.execute("commit;")



    return redirect("/processing")

@app.route("/share/<doc_id>")
@login_required
def shr(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    ppm = can_user_access_doc(r_user_id,doc_id)
    if ppm["write"]==False:
        abort(403)
    sid = id_generator()+id_generator()
    cur.execute("insert into share values ('%s','%s',%s);"%(sid,doc_id,r_user_id))
    cur.execute("commit;")
    return jsonify({"share_id":sid})
    
    
@app.route("/dl/<share_id>")
def shareidtodl(share_id):
    try:
       doc_id = list(list(cur.execute("select doc_id from share where share_id='%s';"%(share_id)))[0])[0]
    except:
        abort(404)
    thumbnail_path = list(list(cur.execute("select file_path from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_name = list(list(cur.execute("select original_name from documents where doc_id='%s'"%(doc_id)))[0])[0]
    original_namee = original_name.rsplit(".",1)[0] +".pdf"
    return send_file(path_or_file=thumbnail_path,download_name=original_namee,as_attachment=True)

@app.route("/api/search/<search_term>",methods=["GET",'POST'])
@login_required
def searchdoc(username,search_term):
    try:
        tlist = request.json["tags"]
    except:
        tlist=[]
    

    


    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    x = list(map(list,cur.execute("select doc_id,snippet(contents,1,'<mark>','</mark>','',3) from contents where file_contents match '%s';"%(search_term))))
    dlist = []
    for d in x:
        hu = list(list(cur.execute("select * from documents where doc_id='%s';"%(d[0])))[0])
        dlist.append(hu)
    doc_list = tuple_to_dict(dlist)
    for i in range(0,len(x)):
        doc_list[i]["search"] = x[i][1]

        
        
    doc_list1 = []
    if len(tlist)==0:
        doc_list1=doc_list
    else:
        for dd in doc_list:
                for tl in dd["tags"]:
                    if tl["tag_name"] in tlist:
                        doc_list1.append(dd)
                        break
        

    doc_list_final = []
    for de in doc_list1:
        opp = can_user_access_doc(r_user_id,de["doc_id"])
        if opp["Read"]:
            doc_list_final.append(de)


    return jsonify({"count":len(x),"results":doc_list_final})



@app.route("/ser/<searchterm>")
@login_required
def sjdhsius(username,searchterm):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]

    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=1);"%(r_user_id)))
    tag_list = []
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = True
        tag_list.append(tag_dict)
    tnames = []
    for tt in tag_list:
        tnames.append(tt["tag_name"])


    return render_template("searchpage.html",tnames=tnames,searchterm=searchterm,tlist=tag_list)


@app.route("/t/<tag_name>")
@login_required
def disag(username,tag_name):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    document_list = tuple_to_dict(list(map(list,cur.execute("select * from documents where owner=%s or doc_id in (select doc_id from tags_ref where tag_id in (select tag_id from usertags where user_id = %s ) )"%(r_user_id,r_user_id)))))
    resulta = []
    for doc in document_list:
        for t in doc["tags"]:
            if t["tag_name"]==tag_name:
                resulta.append(doc)
                break


    
    return jsonify({"count":len(resulta),"results":resulta})


@app.route("/tag/<tag_name>")
@login_required
def rendertags(username,tag_name):
    return render_template("intagsearch.html",searchterm=tag_name)



@app.route("/api/documents/<doc_id>",methods=["GET","POST"])
@login_required
def docapi(username,doc_id):
    if request.method == "GET":
        r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
        access_details = can_user_access_doc(r_user_id,doc_id)
        if(access_details["not_found"]==True):
            abort(404)
        if(access_details["Read"]==False):
            abort(401)
        doc_dict = tuple_to_dict(list(cur.execute("select * from documents where doc_id='%s'"%(doc_id))))[0]
        return jsonify(doc_dict)
    else:
        r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
        if(access_details["not_found"]==True):
            abort(404)
        if(access_details["write"]==False):
            abort(401)
        



        return "updated"

@app.route("/api/permissions/<doc_id>")
@login_required
def permtest(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    
    access_details = can_user_access_doc(r_user_id,doc_id)
    try:
        return jsonify({"write":access_details["write"],"read":access_details["Read"],"owner":access_details["owner"]})
    except:
        abort(404)


@app.route("/api/delete/tag",methods=["POST"])
@login_required
def deltag(username):
    tag_id = request.json["tag_id"]
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    towner = list(list(cur.execute("select owner from tags where tag_id=%s;"%(tag_id)))[0])[0]
    if not towner == r_user_id:
        abort(403)
    cur.execute("delete from tags where tag_id=%s"%(tag_id))
    cur.execute("commit;")
    return "DONE"

@app.route("/api/addusr/tag",methods=["POST"])
@login_required
def addusrtotag(username):
    tag_id = request.json["tag_id"]
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    towner = list(list(cur.execute("select owner from tags where tag_id=%s;"%(tag_id)))[0])[0]
    if not towner == r_user_id:
        abort(403)
    u_id = list(list(cur.execute("select user_id from login where username='%s'"%(request.json["username"])))[0])[0]
    cur.execute("insert into usertags values (%s,%s,%s)"%(tag_id,u_id,request.json["write"]))
    cur.execute("commit")
    return "DONE"

@app.route("/api/ed/tag",methods=["POST"])
@login_required
def addusssrtotag(username):
    print("HI")
    print(request.json["pm"])
    tag_id = request.json["tag_id"]
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    towner = list(list(cur.execute("select owner from tags where tag_id=%s;"%(tag_id)))[0])[0]
    if not towner == r_user_id:
        abort(403)
    tname = request.json["tag_name"]
    pm = request.json["pm"]
    tcolor = request.json["tag_color"]
    cur.execute("update tags set tag_name='%s',tag_color='%s' where tag_id=%s;"%(tname,tcolor,tag_id))
   
    
    for p in pm:
        print(p)
        if int(p[1])==0:
            cur.execute("delete from usertags where tag_id=%s and user_id=%s"%(tag_id,p[0]))
        elif int(p[1])==1:
            cur.execute("update usertags set write=0 where tag_id=%s and user_id=%s"%(tag_id,p[0]))
        elif int(p[1])==2:
            cur.execute("update usertags set write=1 where tag_id=%s and user_id=%s"%(tag_id,p[0]))
    cur.execute("commit;")
    return "DONE"


@app.route("/api/tags")
@login_required
def alltags(username):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=1);"%(r_user_id)))
    tag_list = []
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = True
        tag_list.append(tag_dict)
    
    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=0);"%(r_user_id)))
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = False
        tag_list.append(tag_dict)
    return jsonify(tag_list)




@app.route("/post")
@login_required
def postest(username):
    return render_template("postingtest.html")


@app.route("/sav/doc",methods=["POST"])
@login_required
def asdop(username):
    doc_name = request.json["doc_name"]
    desc = request.json["desc"].strip()
    doc_id = request.json["doc_id"]
    cur.execute("update documents set doc_name='%s',description = '%s' where doc_id='%s';"%(doc_name,desc,doc_id))
    cur.execute("commit;")
    return "UPDATED"



@app.route("/del/t/doc",methods=["POST"])
@login_required
def lksdf(username):
    tag_id = request.json["tag_id"]
    doc_id = request.json["doc_id"]
    cur.execute("delete from tags_ref where doc_id='%s' and tag_id=%s;"%(doc_id,tag_id))
    cur.execute("commit;")
    return "HIIIIII"	
    

@app.route("/add/t/doc",methods=["POST"])
@login_required
def ssds(username):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    doce = request.json["doc_id"]
    tname = request.json["tag_name"]
    tag_id = list(list(cur.execute("select tag_id from tags where tag_name='%s';"%(tname)))[0])[0]
    perm = can_user_access_doc(r_user_id,doce)
    if(perm["write"]==False):
        abort(403)
    wr = list(list(cur.execute("select write from usertags where tag_id=%s and user_id=%s;"%(tag_id,r_user_id)))[0])[0]
    if(wr==0):
        abort(403)
    cur.execute("insert into tags_ref values (%s,'%s');"%(tag_id,doce))
    cur.execute("commit;")
    return "added"



    


@app.route("/tags")
@login_required
def postests(username):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=1);"%(r_user_id)))
    tag_list = []
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = True
        tag_list.append(tag_dict)
    
    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=0);"%(r_user_id)))
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = False
        tag_list.append(tag_dict)
    tnames = []
    for tt in tag_list:
        tnames.append(tt["tag_name"])
    usname = []
    yt={}
    ty={}
    us = list(cur.execute("select username,user_id from login;"))
    for u in us:
        usname.append(list(u)[0])
        yt[list(u)[1]] = usname[-1]
        ty[list(u)[0]] = list(u)[1]
    
    perms = {}
    for tt in tag_list:
        perms[tt["tag_id"]]= []
        res = list(cur.execute("select user_id,write from usertags where tag_id=%s;"%(tt["tag_id"])))
        for r in res:
            ss = list(r)
            if(ss[0]==r_user_id):
                continue
            else:
                perms[tt["tag_id"]].append([ss[0],ss[1]])

    print(perms)
    return render_template("tagtest.html",taglist=tag_list,tnames=tnames,uname = usname,perms=perms,yt=yt,ty=ty)



@app.route("/tags/s/<query>")
@login_required
def tagsearch(username,query):
    qq = '%'+query+'%'
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=1) and tag_name like '%s';"%(r_user_id,qq)))
    tag_list = []
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = True
        tag_list.append(tag_dict)
    
    tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=0) and tag_name like '%s';"%(r_user_id,qq)))
    for tagt in tag_tuples:
        tag_dict={}
        tags = list(tagt)
        tag_dict["tag_id"] = tags[0]
        tag_dict["tag_name"] = tags[1]
        tag_dict["tag_color"] = tags[2]
        tag_dict["owner"] = tags[3]
        tag_dict["write"] = False
        tag_list.append(tag_dict)
    tnames = []
    for tt in tag_list:
        tnames.append(tt["tag_name"])
    usname = []
    yt={}
    ty={}
    us = list(cur.execute("select username,user_id from login;"))
    for u in us:
        usname.append(list(u)[0])
        yt[list(u)[1]] = usname[-1]
        ty[list(u)[0]] = list(u)[1]
    
    perms = {}
    for tt in tag_list:
        perms[tt["tag_id"]]= []
        res = list(cur.execute("select user_id,write from usertags where tag_id=%s;"%(tt["tag_id"])))
        for r in res:
            ss = list(r)
            if(ss[0]==r_user_id):
                continue
            else:
                perms[tt["tag_id"]].append([ss[0],ss[1]])

    print(perms)
    return render_template("tagtest.html",taglist=tag_list,tnames=tnames,uname = usname,perms=perms,yt=yt,ty=ty)




@app.route("/view/doc/<doc_id>")
@login_required
def documentview(username,doc_id):
    r_user_id = list(list(cur.execute("select user_id from login where username='%s'"%(username)))[0])[0]
    perm = can_user_access_doc(r_user_id,doc_id)
    if(perm["not_found"]):
        abort(404)
    elif(not perm["Read"]):
        abort(403)
    else:
        doc =  tuple_to_dict(list(cur.execute("select * from documents where doc_id='%s'"%(doc_id))))[0]
        tag_tuples = list(cur.execute("select * from tags where tag_id in (select tag_id from usertags where user_id=%s and write=1);"%(r_user_id)))
        tag_list = []
        for tagt in tag_tuples:
            tag_dict={}
            tags = list(tagt)
            tag_dict["tag_id"] = tags[0]
            tag_dict["tag_name"] = tags[1]
            tag_dict["tag_color"] = tags[2]
            tag_dict["owner"] = tags[3]
            tag_dict["write"] = True
            tag_list.append(tag_dict)
        tnames = []
        for tt in tag_list:
           tnames.append(tt["tag_name"])
        for ti in doc["tags"]:
            if ti["tag_name"] in tnames:
                tnames.pop(tnames.index(ti["tag_name"]))


        return render_template("view.html",doc_id=doc_id,doc=doc,write=perm["write"],tnames=tnames)
    





app.run(host="0.0.0.0",port=8007)





