import ast
from flask import session,request,abort,redirect
import sqlite3
con = sqlite3.connect('dockat.db',check_same_thread=False) 

cur = con.cursor()





def tuple_to_dict(doc_list):
    result = []
    for doc in doc_list:
        doc_dict = {}
        doc_dict["doc_id"] = doc[0]
        doc_dict["doc_title"] = doc[1]
        doc_dict["desc"] = doc[2]
        doc_dict["owner"] = doc[3]
        doc_dict["tags"] = list(map(list,cur.execute("select tag_id from tags_ref where doc_id='%s';"%(doc[0]))))
        

        tdict = []
        
        for ttt in doc_dict["tags"]:
            tt= ttt[0]
            g = list(cur.execute("select tag_name,tag_color from tags where tag_id=%s;"%(tt)))[0]
            gt = list(g)
            tdi = {}
            tdi["tag_id"] = tt 
            tdi["tag_name"] = gt[0]
            tdi["tag_color"] = gt[1]
            tdict.append(tdi)
        doc_dict["tags"] = tdict




        doc_dict["original_name"]=doc[9]
        result.append(doc_dict)
    return result



def can_user_access_doc(user_id,doc_id):
    try:
        owner_id = list(list(cur.execute("select owner from documents where doc_id='%s';"%(doc_id)))[0])[0]
    except:
        return {"not_found":True}
    if(owner_id==user_id):
        return {"not_found":False,"owner":True,"tag":None,"write":True,"Read":True}
    else:
        tag_ids = list(map(list,cur.execute("select tag_id from tags_ref where doc_id='%s' and tag_id in (select tag_id from usertags where user_id=%s and write=1);"%(doc_id,user_id))))
        if(len(tag_ids)>0):
            return {"not_found":False,"owner":False,"tag":tag_ids[0],"write":True,"Read":True}
        else:
            tag_ids = list(map(list,cur.execute("select tag_id from tags_ref where doc_id='%s' and tag_id in (select tag_id from usertags where user_id=%s and write=0);"%(doc_id,user_id))))
            if(len(tag_ids)>0):
                return {"not_found":False,"owner":False,"tag":tag_ids[0],"write":False,"Read":True}
            else:
                return {"not_found":False,"owner":False,"tag":None,"write":False,"Read":False}