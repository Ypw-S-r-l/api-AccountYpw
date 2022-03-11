from datetime import datetime
from xmlrpc.client import DateTime
from sqlalchemy import DATETIME, JSON, TEXT, VARCHAR, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP
from Database.conexion import meta, engine

#------- Creacion de la tabla 'users'
users = Table(
    "users", meta,
    Column('userID', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('username', String(255)), #Mandatory
    Column('password', String(255)), #Mandatory
    Column('name', String(255)), #Mandatory
    Column('email', String(255)), #Mandatory
    Column('phone', String(255), nullable=True),
    Column('dateOfBirth', String(255), nullable=True),
    Column('language', String(255), nullable=True),
    Column('country', String(255), nullable=True),
    Column('ypwCashBalance', String(255), nullable=True),
    Column('shippingAddress', String(255), nullable=True),
    Column('registrationDate', String(255), nullable=True),
    Column('identificationCard', String(255), nullable=True),
    Column('accountUpdateDate', String(255), nullable=True),
    Column('accountVersion', String(255), nullable=True),
    Column('timeZone', String(255), nullable=True),
    Column('recoveryCode', String(255), nullable=True),
    Column('applications', String(255), nullable=True),
    Column('limitations', String(255), nullable=True),
    Column('accountType', String(255), nullable=True),
    Column('tradingExits', String(255), nullable=True),
    Column('pendingInvoices', String(255), nullable=True),
    Column('bills', String(255), nullable=True),
    Column('subscriptions', String(255), nullable=True),
    Column('metodoPago', String(255), nullable=True),
    Column('servidorDB', String(255), nullable=True),
    Column('userDB', String(255), nullable=True),
    Column('puertoDB', String(255), nullable=True),
    Column('pagWeb', String(255), nullable=True),
    Column('keyUser', String(255), unique=True)
)

meta.create_all(engine)     #Creando todo, las tablas, funciones, etc
