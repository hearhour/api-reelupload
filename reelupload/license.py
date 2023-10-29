
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, status
from connection import get_mysql
from connection import get_mysql_LD
from connection import get_mysql_farmreel
import requests
from datetime import datetime, timedelta
from datetime import date
import random
import json
import string
import os
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import FileResponse


router = APIRouter()

def generate_random_text():
    letters = string.ascii_lowercase
    random_text = ''.join(random.choice(letters) for _ in range(8)) + ''.join(random.choice(string.digits) for _ in range(5))
    return random_text


@router.get("/status")
def status():
    return True

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
    
@router.get("/get_current_date")
def get_current_date():
    current_date = date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    return formatted_date

@router.get("/license_update")
def license_update():
    try:
        info = {'version': '4.0.8', 'info': ['Fixed Post Scheduled', 'Update Limit Post']}
        return info
    except:
        return None
    

@router.get("/insertkey")
def insertkey(license, buykey):
    try:
        print(buykey)
        datenow = requests.get('https://mmoshop.me/datenow.php').text
        now = datetime.strptime(datenow, '%Y-%m-%d').date()
        if 'REEL1UPLOAD' in buykey:
            expire_date = now + timedelta(days=31)
        if 'REEL3UPLOAD' in buykey:
            expire_date = now + timedelta(days=93)
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

@router.get("/buykey")
def buykey(token: int, month: int):
    if token == 3991:
        if month == 1:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(18)))
            Key = 'REEL1UPLOAD' + result_str
        elif month == 3:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(18)))
            Key = 'REEL3UPLOAD' + result_str
        db = get_mysql()
        cursor = db.cursor(dictionary=True)
        insert_query = "INSERT INTO reeluploadv3 (buykey) VALUES (%s)"
        cursor.execute(insert_query, (Key,))
        db.commit()
        print(Key)
        return {"Buykey": Key}
    else:
        return 'Token not valid'



@router.get("/ld_datakey")
def ld_read_rootsss(license):
    try:
        db = db = get_mysql_LD()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM licenses WHERE license = %s", (license,))
        rows = cursor.fetchone()
        print(rows)
        return rows
    except:
        return None

@router.get("/ld_insertkey")
def ld_insertkey(license: str):
    try:
        datenow = requests.get('https://mmoshop.me/datenow.php').text
        now = datetime.strptime(datenow, '%Y-%m-%d').date()

        start_date = now.strftime('%Y-%m-%d')
        print(start_date)
        db = get_mysql_LD()
        cursor = db.cursor(dictionary=True)

        insert_query = "INSERT INTO licenses (license, start) VALUES (%s, %s)"  # Replace 'licenses' with your actual table name
        cursor.execute(insert_query, (license, start_date))
        db.commit()

        cursor.close()
        db.close()
        return {"message": "License value inserted successfully."}
    except Exception as e:
        return {"message": f"An error occurred: {e}"}
    
    
@router.get("/status_ld")
def status_ld():
    return {'status' : 'farmreel'}


#Farm Reel
@router.get("/farmreel/user")
def farmreel_user(license):
    try:
        db = db = get_mysql_farmreel()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE license = %s", (license,))
        rows = cursor.fetchone()
        cursor.close()
        return rows
    except:
        return None

@router.get("/farmreel/insertkey")
def farmreel_insertkey(license, buykey):
    if license == 'LDREEL7E8C8CA1038D04832460C68782EFF0D8':
        return {"data": "Unknow License"}
    try:
        datenow = requests.get('https://mmoshop.me/datenow.php').text
        now = datetime.strptime(datenow, '%Y-%m-%d').date()
        if 'FARMREEL1' in buykey:
            expire_date = now + timedelta(days=31)
        if 'FARMREEL3' in buykey:
            expire_date = now + timedelta(days=93)
        if 'FREE' in buykey:
            expire_date = now + timedelta(days=2)
        start_date = now.strftime('%Y-%m-%d')
        expire_date = expire_date.strftime('%Y-%m-%d')

        db = get_mysql_farmreel()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE buykey = %s", (buykey,))
        checkbuykey = cursor.fetchone()
        if checkbuykey is None:
            db.close()
            return {"data": "Unknow License"}
        else:
            cursor.execute("SELECT * FROM users WHERE license = %s", (license,))
            result = cursor.fetchone()
            if result is None:
                update_query = "UPDATE users SET license = %s, start_date = %s, expire_date = %s, note = %s WHERE buykey = %s AND license = ''"
                cursor.execute(update_query, (license, start_date, expire_date, '10', buykey))
                db.commit()
                db.close()
                if cursor.rowcount > 0:
                    return {"data": 'success'}
                else:
                    return {"data": "License already exists"}
            else:
                db.close()
                return {"data": "License already exists"}
    except:
        pass
        

@router.get("/farmreel/updateexpire")
def update_expire(license):
    try:
        random_text = generate_random_text()
        db = get_mysql_farmreel()
        cursor = db.cursor(dictionary=True)
        update_query = "UPDATE users SET license = %s WHERE license = %s"
        cursor.execute(update_query, (str(license) + 'expirekey_' + random_text, license))
        db.commit()
        db.close()
        return {"data": "update success"}
    except Exception as e:
        print(e)
        return None


@router.get("/farmreel/buykey", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
def buykey(token: int, month: int, note: str = '', name: str = ''):
    if token == 3991:
        if month == 1:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(15)))
            Key = 'FARMREEL1' + result_str
        elif month == 3:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(15)))
            Key = 'FARMREEL3' + result_str
        elif month == 0:
            result_str = ''.join((random.choice('ABCDFGHJIKLMNOPQRSTUVWXYZ1234567890') for i in range(15)))
            Key = 'FREE' + result_str
        db = get_mysql_farmreel()
        cursor = db.cursor(dictionary=True)
        insert_query = "INSERT INTO users (buykey, note, name) VALUES (%s, %s, %s)"  # Add "note" field
        cursor.execute(insert_query, (Key, note, name))  # Pass the "note" parameter
        db.commit()
        print('')
        return {"Buykey": Key}
    else:
        return 'Token not valid'

@router.get("/farmreel/changekey", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
def farmreel_change(old_license, new_license):
    db = get_mysql_farmreel()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT changekey, start_date, expire_date FROM users WHERE license = %s", (old_license,))
    checkbuykey = cursor.fetchone()
    if checkbuykey:
        try:
            start_date = checkbuykey['start_date']
            expire_date = checkbuykey['expire_date']
            difference = (expire_date - start_date).days

            if difference <= 31:
                if checkbuykey and checkbuykey['changekey'] < 2:
                    new_changekey = checkbuykey['changekey'] + 1
                    cursor.execute("UPDATE users SET changekey = %s WHERE license = %s", (new_changekey, old_license))
                    db.commit()
                    update_query = "UPDATE users SET license = %s WHERE license = %s"
                    cursor.execute(update_query, (new_license, old_license))
                    db.commit()
                    db.close()
                    return {"detail": "Change success"}
                
                elif checkbuykey['changekey'] >= 2:
                    db.close()
                    return {"detail": "Change limit exceeded"}
            else:
                if checkbuykey and checkbuykey['changekey'] < 6:
                    new_changekey = checkbuykey['changekey'] + 1
                    cursor.execute("UPDATE users SET changekey = %s WHERE license = %s", (new_changekey, old_license))
                    db.commit()
                    update_query = "UPDATE users SET license = %s WHERE license = %s"
                    cursor.execute(update_query, (new_license, old_license))
                    db.commit()
                    db.close()
                    return {"detail": "Change success"}
                elif checkbuykey['changekey'] >= 6:
                    db.close()
                    return {"detail": "Change limit exceeded"}
        except Exception as e:
            print("Error", e)
    if checkbuykey is None:
        db.close()
        return {"detail": "Unknown License"}


@router.post("/farmreel/uploadfile/", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def upload_file(token:int ,file: UploadFile):
    if token == 3991:
        try:
            with open('version/' + file.filename, "wb") as f:
                f.write(file.file.read())
            return {"message": "File uploaded successfully"}
        except Exception as e:
            return {"error": str(e)}
    else:
        return 'Token not valid'
        
@router.delete("/farmreel/deletefile/{filename}", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def delete_file(token: int, filename: str):
    if token == 3991:
        try:
            # Specify the path to the file
            file_path = 'version/' + filename

            # Check if the file exists
            if os.path.exists(file_path):
                os.remove(file_path)
                return {"message": f"File {filename} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail="File not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))    
    else:
        return 'Token not valid'

def update_json_file(version: str, info: list):
    file_path = "version/version.json"  # Adjust the file path as needed
    try:
        # Read the existing JSON data
        with open(file_path, "r") as json_file:
            existing_data = json.load(json_file)

        # Update the data
        existing_data["version"] = version

        # Split comma-separated strings into individual strings
        for i, item in enumerate(info):
            info[i] = item.split(',')

        # Flatten the list of lists into a single list
        existing_data["info"] = [item for sublist in info for item in sublist]

        # Write the updated data back to the file
        with open(file_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)

        return {"message": f"JSON file '{file_path}' updated successfully"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/farmreel/checkfile/")
async def check_exe_files():
    try:

        files = os.listdir('version/')
        exe_files = [file for file in files if file.endswith(".exe")]
        if exe_files:
            return {"message": f"{len(exe_files)} .exe file(s) found in the 'version/' directory", "files": exe_files}
        else:
            return {"message": "No .exe files found in the 'version/' directory"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/farmreel/version/json")
async def check_exe_files():
    try:
        files = os.listdir('version/')
        exe_files = [file for file in files if file.endswith(".json")]
        if exe_files:
            data = []
            for file in exe_files:
                with open(os.path.join('version', file), 'r') as f:
                    content = json.load(f)
                    data.append(content)
            return {"message": f"{len(exe_files)} .json file(s) found in the 'version/' directory", "data": data}
        else:
            return {"message": "No .json files found in the 'version/' directory"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Define the route to update the JSON file
@router.post("/farmreel/update_version/")
async def update_version_endpoint(version: str = Form(...), info: list = Form(...)):
    result = update_json_file(version, info)
    return result


@router.get("/farmreel/download_zip")
async def download_zip_file():
    try:
        # Adjusting the path to the 'setup.zip' file based on the directory structure
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_zip_file = os.path.join(script_dir, "version", "setup.zip")

        # Check if the file exists
        if not os.path.exists(path_to_zip_file):
            return Response(content="File not found", status_code=status.HTTP_404_NOT_FOUND)

        # Set the appropriate MIME type for .zip
        mime_type = 'application/zip'

        # Return the file to be downloaded
        return FileResponse(path_to_zip_file, media_type=mime_type, filename="setup.zip")

    except FileNotFoundError as e:
        return Response(content="File not found", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
@router.get("/api")
def read_root(tracking):
    print(tracking)
    return {
        'Product_Name' : 'Flipper Zero',
        'price' : '160.50 USD Our free (included)',
        'location' : 'Toulkrok, Pnhom Penh',
        'kg' : '3 KG',
        'History' : [
            {'process' : 'Package collection',
            'location' : 'Chroy Chva',},
            {'process' : 'Package arrived at center',
            'location' : 'Toul songkae',},
            {'process' : 'Delivery scan',
            'location' : 'Ressey Keo',},
            {'process' : 'Package delivery',
            'location' : 'Toul krok',}
        ]
    }

@router.get("/")
async def index():
    return {"msg": "Hello World"}

