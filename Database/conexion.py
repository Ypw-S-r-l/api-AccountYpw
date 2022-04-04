import pymysql
from sqlalchemy import *
from sqlalchemy import create_engine, MetaData

#dbConnection= MySQLdb.connect(user='ypwLoginApi', password='dfz0U!M7PwXx', host='127.0.0.1', database='ypwLogin')
URL = "mysql+pymysql://ypwLoginApi:dfz0U!M7PwXx@ypw.com.do/ypwLogin"

engine = create_engine(URL)
meta = MetaData()   #Para enviar propiedades a la tabla 'users'
conn = engine.connect()   #Conectando engine a base de datos
#cursor = conn.cursor()