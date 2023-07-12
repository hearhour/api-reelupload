
from fastapi import APIRouter
from connection import get_mysql
import requests
from datetime import datetime, timedelta
import random
import string

router = APIRouter()

def generate_random_text():
    letters = string.ascii_lowercase
    random_text = ''.join(random.choice(letters) for _ in range(8)) + ''.join(random.choice(string.digits) for _ in range(5))
    return random_text


@router.get("/datakey")
def read_rootsss(license):
    try:
        db = db = get_mysql()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reeluploadv3 WHERE license = %s", (license,))
        rows = cursor.fetchone()
        print(rows)
        return rows
    except:
        return None
    

@router.get("/insertkey")
def insertkey(license, buykey):
    try:
        print(buykey)
        datenow = requests.get('https://mmoshop.me/datenow.php').text
        now = datetime.strptime(datenow, '%Y-%m-%d').date()
        expire_date = now + timedelta(days=31)
        start_date = now.strftime('%Y-%m-%d')
        expire_date = expire_date.strftime('%Y-%m-%d')

        db = get_mysql()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM reeluploadv3 WHERE buykey = %s", (buykey,))
        checkbuykey = cursor.fetchone()
        if checkbuykey is None:
            print('no')
            db.close()
            return {"data": "Unknow License"}
        else:
            print('yes')
            cursor.execute("SELECT * FROM reeluploadv3 WHERE license = %s", (license,))
            result = cursor.fetchone()
            if result is None:
                update_query = "UPDATE reeluploadv3 SET license = %s, start = %s, expire = %s, note = %s WHERE buykey = %s AND license = ''"
                cursor.execute(update_query, (license, start_date, expire_date, '10', buykey))
                db.commit()
                db.close()
                if cursor.rowcount > 0:
                    return {"data": 'success'}
                else:
                    return {"data": "License field is not empty"}
            else:
                db.close()
                return {"data": "License already exists"}
    except:
        pass
        
@router.get("/updateexpire")
def update_expire(license):
    try:
        random_text = generate_random_text()
        db = get_mysql()
        cursor = db.cursor(dictionary=True)
        update_query = "UPDATE reeluploadv3 SET license = %s WHERE license = %s"
        cursor.execute(update_query, (str(license) + 'expirekey_' + random_text, license))
        db.commit()
        db.close()
        return {"data": "update success"}
    except Exception as e:
        print(e)
        return None

