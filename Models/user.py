from sqlalchemy import JSON, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, Boolean
from Database.conexion import meta, engine

# ------- Creacion de la tabla 'users' y 'keys'
users = Table(
    "users", meta,
    Column('userID', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('username', String(35), nullable=False, unique=True),
    Column('password', String(50), nullable=False),
    Column('name', String(50), nullable=False),
    Column('email', String(65), nullable=False, unique=True),
    Column('phone', String(20), nullable=True),
    Column('dateOfBirth', String(50), nullable=True),
    Column('language', String(50), nullable=True),
    Column('country', String(50), nullable=True),
    Column('ypwCashBalance', String(255), nullable=True),
    Column('shippingAddress', JSON, nullable=True),
    Column('registrationDate', TIMESTAMP, nullable=True),
    Column('identificationCard', String(20), nullable=True),
    Column('accountUpdateDate', TIMESTAMP, nullable=True),
    Column('accountVersion', String(20), nullable=True),
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
    Column('data', JSON, nullable=True),
    Column('codetmp', Integer, nullable=True),
    Column('block', Boolean, nullable=True),
    Column('developer', Boolean, nullable=True),
    Column('inBlock', Boolean, nullable=True),
    Column('numberCode', Integer, nullable=True)
)


keys = Table(
    'keys', meta,
    Column('userID', Integer, primary_key=True, nullable=False),
    Column('keyUser', String, nullable=False),
    Column('appConnect', String(255), nullable=False),
    Column('keyID', Integer, nullable=False)
)


apiKey = Table(
    'apiKey', meta,
    Column('id', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('globalUser', String(), nullable=False),
    Column('CLIENT_KEY', String(), nullable=False),
    Column('CLIENT_SECRET', String(), nullable=False),
    Column('baseUrl', String(), nullable=True),
    Column('permissions', String(100), nullable=False)
)

dataTable = Table(
    'data', meta,
    Column('idData', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('userID', Integer, nullable=False),
    Column('keyData', String, nullable=False),
    Column('Data', JSON, nullable=False)
)

meta.create_all(engine)  # Creando todo, las tablas, funciones, etc
