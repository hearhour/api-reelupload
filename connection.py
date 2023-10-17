import mysql.connector

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}".format(
            "farmreel", "RIsnb&j!!.mH", "184.168.98.120", "3306", "farmreel"
        )
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



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
    
def get_mysql_farmreel():
    mydb = None
    try:
        mydb = mysql.connector.connect(
            host="184.168.98.120",
            user="farmreel",
            password="RIsnb&j!!.mH",
            port="3306",
            database="farmreel"
        )
        return mydb
    except:
        return None
