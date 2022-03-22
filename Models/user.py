from datetime import datetime
from sqlalchemy import DATETIME, JSON, TEXT, VARCHAR, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, DateTime
from Database.conexion import meta, engine

#------- Creacion de la tabla 'users'
users = Table(
    "users", meta,
    Column('userID', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('username', String(35), nullable=True), #Mandatory
    Column('password', String(50), nullable=True), #Mandatory
    Column('name', String(50), nullable=True), #Mandatory
    Column('email', String(65), nullable=True), #Mandatory
    Column('phone', String(20), nullable=True),
    Column('dateOfBirth', String(50), nullable=True),
    Column('language', String(50), nullable=True),
    Column('country', String(50), nullable=True),
    Column('ypwCashBalance', String(255), nullable=True),
    Column('shippingAddress', JSON, nullable=True),
    Column('registrationDate', TIMESTAMP, nullable=True),
    Column('identificationCard', String(20), nullable=True),
    Column('accountUpdateDate', TIMESTAMP, nullable=True),
    Column('accountVersion', String(5), nullable=True),
    Column('timeZone', String(50), nullable=True),
    Column('recoveryCode', String(255), nullable=True),
    Column('applications', JSON, nullable=True),
    Column('limitations', JSON, nullable=True),
    Column('accountType', String(25), nullable=True),
    Column('tradingExits', JSON, nullable=True),
    Column('pendingInvoices', JSON, nullable=True),
    Column('bills', JSON, nullable=True),
    Column('subscriptions', JSON, nullable=True),
    Column('metodoPago', String(25), nullable=True),
    Column('servidorDB', String(255), nullable=True),
    Column('userDB', String(25), nullable=True),
    Column('puertoDB', String(255), nullable=True),
    Column('pagWeb', String(255), nullable=True),
    Column('keyUser', String(255), unique=True)
)

meta.create_all(engine)     #Creando todo, las tablas, funciones, etc
