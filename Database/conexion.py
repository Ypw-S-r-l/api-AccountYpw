import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine

URL = "mysql+pymysql://ypwLoginApi:dfz0U!M7PwXx@ypw.com.do/ypwLogin"


engine = sa.create_engine(URL,
                          echo=False,
                          pool_pre_ping=True,
                          pool_recycle=3600)
meta = sa.MetaData()   #Para enviar propiedades a la tabla 'users'.
conn = engine.connect()   #Conectando engine a base de datos.
cursor= conn.connection.cursor()    #Creando la conexion a cursor para tener acceso a la propiedad cursor.