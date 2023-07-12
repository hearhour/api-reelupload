import mysql.connector

def get_mysql():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            host="184.168.98.120",
            user="reelupload",
            password="U%3Xq2JNQ(ef",
            port="3306",
            database="reelupload"
        )
        return mydb
    except:
        return None

