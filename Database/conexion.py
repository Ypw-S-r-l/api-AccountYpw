import asyncio
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData
#from sqlalchemy.ext.asyncio import create_async_engine

URL = "mysql+pymysql://ypwLoginApi:dfz0U!M7PwXx@ypw.com.do/ypwLogin"

engine = create_engine(URL)
meta = sa.MetaData()   #Para enviar propiedades a la tabla 'users'
conn = engine.connect()   #Conectando engine a base de datos
#cursor = conn.cursor()
