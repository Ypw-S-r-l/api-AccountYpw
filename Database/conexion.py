from sqlalchemy import *
from sqlalchemy import create_engine, MetaData

URL = "mysql+pymysql://root:admin@localhost:3306/apilogin"
engine = create_engine(URL)

meta = MetaData()   #Para enviar propiedades a la tabla 'users'

conn = engine.connect() #Conectando engine a base de datos
