from unittest import result
from celery import Celery
import random
import string
import sqlite3
from config import *
con = sqlite3.connect('dockat.db',check_same_thread=False)
import hashlib
cur = con.cursor()


def checkhash(file_name):
    with open(file_name, 'rb') as file_to_check:
    
        data = file_to_check.read()    
    
        md5_returned = hashlib.md5(data).hexdigest()
    return md5_returned


import os
CELERY_BROKER_URL='redis://localhost:6379'
result_backend='redis://localhost:6379'

celery = Celery('tasks',backend=result_backend ,broker=CELERY_BROKER_URL)

def id_generator():

    random_id =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    while len(list(cur.execute("SELECT doc_id FROM documents where doc_id='%s';" %(random_id)))):
        random_id =  ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    return random_id


def randonfile():
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=10))




@celery.task
def processdoc(f_id,temp_filelocation,username):
    
    if((os.path.splitext(temp_filelocation)[1] not in ['.pdf','.PDF'])):
       
        temp_filename = randonfile() + ".pdf"
        os.system("img2pdf %s -o %s" %(temp_filelocation,temp_folder+'/'+temp_filename))
        os.system("ocrmypdf --rotate-pages --sidecar %s -l eng+guj+hin %s %s" %(temp_folder+'/'+f_id+'.txt',temp_folder+'/'+temp_filename,media_folder+"/"+username+"/"+f_id+'.pdf'))
        os.remove(os.path.join(temp_folder,temp_filename))
    
    else:
        
        os.system("ocrmypdf --force-ocr --rotate-pages --sidecar %s -l eng+guj+hin %s %s" %(temp_folder+'/'+f_id+'.txt',temp_filelocation,media_folder+'/'+username+"/"+f_id+'.pdf'))
    os.system('mv %s %s' %(temp_filelocation,(consume_folder+'/'+username+"/"+temp_filelocation.split('/')[-1])))
    with open(os.path.join(temp_folder,f_id+'.txt')) as f:
        acontents = f.readlines()
    contents=''
    for lines in acontents:
        contents +=lines
    os.remove((os.path.join(temp_folder,f_id+'.txt')))
    cur.execute("INSERT INTO CONTENTS VALUES ('%s','%s');" %(f_id,contents.strip()))
    md5_for_pdf = checkhash(os.path.join(media_folder,username,f_id+'.pdf'))
    md5_for_original = checkhash(os.path.join(consume_folder,username,temp_filelocation.split('/')[-1]))
    os.system("convert -thumbnail 500x -background white -alpha remove %s[0] %s-thumbnail.png"%((os.path.join(media_folder,username,f_id+'.pdf')),media_folder+'/'+'thumbnails'+'/'+f_id))


    cur.execute("update documents set md5_checksum='%s',original_md5='%s',file_path='%s',original_path='%s' where doc_id='%s';" %(md5_for_pdf,md5_for_original,(os.path.join(media_folder,username,f_id+'.pdf')),(os.path.join(consume_folder,username,temp_filelocation.split('/')[-1])),f_id))
    cur.execute("commit;")
    print("task DOne")


