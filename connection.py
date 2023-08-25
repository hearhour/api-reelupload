import mysql.connector

def get_mysql():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            host="184.168.98.120",
            user="reeluploadv4",
            password="rp[Tbgtr(xbu",
            port="3306",
            database="reeluploadv4"
        )
        return mydb
    except:
        return None


def get_mysql_LD():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            host="184.168.98.120",
            user="reeluploadv4",
            password="rp[Tbgtr(xbu",
            port="3306",
            database="ld_reelupload"
        )
        return mydb
    except:
        return None
