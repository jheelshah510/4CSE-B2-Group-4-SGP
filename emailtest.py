from imap_tools import MailBox, AND
from config import temp_folder
from tasks import id_generator
import time
from tasks import processdoc
import os
import sqlite3
con = sqlite3.connect('dockat.db',check_same_thread=False) 

cur = con.cursor()
username = 'tarang'

mb = MailBox("webmail.tarang.uk").login("test@dockat.tarang.uk", "Raspberry18")
while True:
    messages = mb.fetch(criteria=AND(seen=False),
                            mark_seen=True,
                            bulk=True)


    for m in messages:
        for att in m.attachments:
        
            if att.filename.lower().endswith(('.pdf','.jpg','.jpeg')):
                fname = att.filename.lower()
                f_id = id_generator()
                print("HI")
                tem_path = os.path.join(temp_folder,f_id+"."+(fname.split('.')[-1]))
                with open(tem_path, 'wb') as f:
                    f.write(att.payload)
                processdoc.delay(f_id,tem_path,username)
                doc_user_id = list(list(cur.execute("select user_id from login where username='%s';"%(username)))[0])[0]
                cur.execute("insert into documents values ('%s','%s',%s,%s,'%s',%s,%s,%s,%s,'%s');" %(f_id,(fname.rsplit(".",1)[0]),"NULL",str(doc_user_id),"[]","NULL","NULL","NULL","NULL",fname)) 
                cur.execute("commit;")
    time.sleep(300)