
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response, status, Request
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
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
from fastapi.middleware.cors import CORSMiddleware

import random
import os
import io

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
    return {'status' : 'farmreelv2'}


#Farm Reel
@router.get("/farmreel/user")
def farmreel_user(license):
    try:
        db = get_mysql_farmreel()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE license = %s", (license,))
        rows = cursor.fetchone()
        cursor.close()
        return rows
    except:
        return None
    

@router.get("/farmreelv2/user")
def farmreel_user(license: str, head : str):
    try:
        if head == 'apireel':
            db = get_mysql_farmreel()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE license = %s", (license,))
            rows = cursor.fetchone()
            cursor.close()
            return rows
        else:
            return None
    except Exception as e:
        return None


@router.get("/farmreel/insertkey")
def farmreel_insertkey(license, buykey):
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


@router.post("/farmreel/uploadfile/")
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
    if tracking == '0123456789':
        return {
        'Product_Name' : 'Online Shop',
        'price' : '10.50 USD Our free (included)',
        'location' : 'Psa Tmey, Pnhom Penh',
        'kg' : '5 KG',
        'History' : [
            {'process' : 'Package collection',
            'location' : 'Psa Tmey',
            'time' : '07:00 AM'}
        ]
    }
    if tracking == '012345678':
        return {
        'Product_Name' : 'Online Shop',
        'price' : '10.50 USD Our free (included)',
        'location' : 'Psa Tmey, Pnhom Penh',
        'kg' : '5 KG',
        'History' : [
            {'process' : 'Package collection',
            'location' : 'Psa Tmey',
            'time' : '07:00 AM'},
            {'process' : 'Package arrived at center',
            'location' : 'Toul songkae',
            'time' : '09:00 AM'},
        ]
    }
    return {
        'Product_Name' : 'Flipper Zero',
        'price' : '160.50 USD Our free (included)',
        'location' : 'Toulkrok, Pnhom Penh',
        'kg' : '3 KG',
        'History' : [
            {'process' : 'Package collection',
            'location' : 'Chroy Chva',
            'time' : '07:00 AM'},
            {'process' : 'Package arrived at center',
            'location' : 'Toul songkae',
            'time' : '09:00 AM'},
            {'process' : 'Delivery scan',
            'location' : 'Ressey Keo',
            'time' : '12:00 AM'},
            {'process' : 'Package delivery',
            'location' : 'Toul krok',
            'time' : '02:00 PM'}
        ]
    }

@router.get("/")
async def index():
    return {"msg": "Hello World"}


@router.get("/tiktok/allvideos")
def getVideosByUsername(username : str, max_cursor= None):

    dd = requests.get(f'https://www.tiktok.com/{username}').text
    try:
        authorSecId = dd.split('"authorSecId":"')[1].split('"')[0]
    except:
        try:
            authorSecId = dd.split('"secUid":"')[1].split('"')[0]
        except:
            return None
    #global i
    i = 0
    if max_cursor is None:
        max_cursor = '0'
    headers = {
        'host': 'api22-core-c-alisg.tiktokv.com',
        'sdk-version': '2',
        'x-ss-req-ticket': '1699790586124',
        'passport-sdk-version': '19',
        'x-tt-dm-status': 'login=0;ct=1;rt=6',
        'x-vc-bdturing-sdk-version': '2.3.4.i18n',
        'x-tt-store-region': 'kh',
        'x-tt-store-region-src': 'did',
        'user-agent': 'com.zhiliaoapp.musically/2023201050 (Linux; U; Android 12; en_US; SM-G9500; Build/V417IR;tt-ok/3.12.13.4-tiktok)',
        'x-ladon': 'Pr1sNnemlziIwGGw0vOP/IRuy4mg1vFJgJqpaF1CjHXcJ9Vw',
    }

    response = requests.get(
        'https://api22-core-c-alisg.tiktokv.com/aweme/v1/aweme/post/?source=0&user_avatar_shrink=144_144&video_cover_shrink=372_495&'
        f'max_cursor={max_cursor}&'
        f'sec_user_id={authorSecId}'
        '&count=20&sort_type=0&iid=7300544687662728965&device_id=7300543548435318277&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=320105&version_name=32.1.5&device_platform=android&os=android&ab_version=32.1.5&ssmix=a&device_type=SM-G9500&device_brand=Samsung&language=en&os_api=32&os_version=12',
        headers=headers).json()

    try:
        videos = response['aweme_list']
        # print(videos[0]['video']['ai_dynamic_cover']['url_list'][-1])
        # print(videos)
        all_videos = []
        for video in videos:
            data = video['video']['play_addr']['url_list']
            cover = video['video']['ai_dynamic_cover']['url_list'][-1]
            title = video['desc']
            play_count = video['statistics']['play_count']
            i += 1
            #print({'row': i ,'url_video' : data[-1], 'cover' : cover, 'title' : title})
            all_videos.append({'row': i ,'url_video' : data[-1], 'cover' : cover, 'title' : title, 'play_count':play_count})
        try:
            max_cursor = response['max_cursor']
            return {'videos' : all_videos, 'max_cursor':max_cursor}
            # print(max_cursor)
        except:
            pass
    except:
        return {'videos' : None, 'max_cursor': None}


@router.get("/generate_profile")
async def generate_image_api(text: str, size: tuple = (1000, 1000)):
    logo_folder = 'logo'
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    draw.rectangle([0, 0, size[0], size[1]], fill=bg_color)
    font_size = 100
    font_color = (255, 255, 255)
    font_path = 'BostonBold.otf'
    font = ImageFont.truetype(font_path, font_size)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]



    x = (size[0] - text_width) // 2
    y_text = (size[1] - text_height) // 2
    logo_files = [f for f in os.listdir(logo_folder) if f.endswith('.png')]

    if logo_files:
        logo_file = random.choice(logo_files)
        logo_path = os.path.join(logo_folder, logo_file)
        logo = Image.open(logo_path).convert('RGBA')
        x_logo = (size[0] - logo.width) // 2
        y_logo = y_text - logo.height - 10
        image.paste(logo, (x_logo, y_logo), logo)

    draw.text((x, y_text), text, font=font, fill=font_color)

    # Create an in-memory buffer
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)

    # Return the image as a streaming response
    return StreamingResponse(io.BytesIO(img_byte_array.read()), media_type="image/png")


def download_video(url):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        return StreamingResponse(io.BytesIO(response.content), media_type="video/mp4")
    else:
        return StreamingResponse(io.BytesIO(b"Failed to download video"), media_type="text/plain")



@router.get("/get_video")
async def get_video(video_url):
    return download_video(video_url)


@router.get("getvideos/tiktok")
def getVideosByUsernames(username : str, request: Request, max_cursor= None):
    
    client_host = request.headers.get("origin")
    # print(vars(request))
    # print("CLIENT HOST", client_host)
    if str(client_host) != "https://tiktok.mmoshop.me": return {'videos' : None, 'max_cursor': None}

    dd = requests.get(f'https://www.tiktok.com/{username}').text
    try:
        authorSecId = dd.split('"authorSecId":"')[1].split('"')[0]
    except:
        try:
            authorSecId = dd.split('"secUid":"')[1].split('"')[0]
        except:
            return None
    #global i
    i = 0
    if max_cursor is None:
        max_cursor = '0'
    headers = {
        'host': 'api22-core-c-alisg.tiktokv.com',
        'sdk-version': '2',
        'x-ss-req-ticket': '1699790586124',
        'passport-sdk-version': '19',
        'x-tt-dm-status': 'login=0;ct=1;rt=6',
        'x-vc-bdturing-sdk-version': '2.3.4.i18n',
        'x-tt-store-region': 'kh',
        'x-tt-store-region-src': 'did',
        'user-agent': 'com.zhiliaoapp.musically/2023201050 (Linux; U; Android 12; en_US; SM-G9500; Build/V417IR;tt-ok/3.12.13.4-tiktok)',
        'x-ladon': 'Pr1sNnemlziIwGGw0vOP/IRuy4mg1vFJgJqpaF1CjHXcJ9Vw',
    }

    response = requests.get(
        'https://api22-core-c-alisg.tiktokv.com/aweme/v1/aweme/post/?source=0&user_avatar_shrink=144_144&video_cover_shrink=372_495&'
        f'max_cursor={max_cursor}&'
        f'sec_user_id={authorSecId}'
        '&count=20&sort_type=0&iid=7300544687662728965&device_id=7300543548435318277&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=320105&version_name=32.1.5&device_platform=android&os=android&ab_version=32.1.5&ssmix=a&device_type=SM-G9500&device_brand=Samsung&language=en&os_api=32&os_version=12',
        headers=headers).json()

    try:
        videos = response['aweme_list']
        # print(videos[0]['video']['ai_dynamic_cover']['url_list'][-1])
        # print(videos)
        all_videos = []
        for video in videos:
            data = video['video']['play_addr']['url_list']
            cover = video['video']['ai_dynamic_cover']['url_list'][-1]
            title = video['desc']
            play_count = video['statistics']['play_count']
            i += 1
            #print({'row': i ,'url_video' : data[-1], 'cover' : cover, 'title' : title})
            all_videos.append({'row': i ,'url_video' : data[-1], 'cover' : cover, 'title' : title, 'play_count':play_count})
        try:
            max_cursor = response['max_cursor']
            return {'videos' : all_videos, 'max_cursor':max_cursor}
            # print(max_cursor)
        except:
            pass
    except:
        return {'videos' : None, 'max_cursor': None}
