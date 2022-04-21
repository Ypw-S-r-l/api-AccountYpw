from http.client import HTTPException
import jwt, re, secrets, base64
from fastapi import APIRouter
from bs4 import BeautifulSoup
from sqlalchemy import false, text
from Database.conexion import conn as connection
from Models.index import users, keys
from Schemas.schemas import UserLogin, UserObtener, UserRegistro
from datetime import datetime
from cryptography.fernet import Fernet

user = APIRouter()


@user.on_event("startup")
async def startup():
    connection.connect()


#--------- ruta: root ---------
@user.get('/', tags=["Welcome"])
async def root():
    return {"message": "Bienvenidos a APILogin YPW"}


#Y comprobamos si los inputs estan vacios
def verificarVacio(x):
    for i in x.values():
        if len(i) == 0:
            return True
        else:
            return False

#Para generar keyUser
key= Fernet.generate_key()
f= Fernet(key)

#--------- ruta: OBTENER DATOS ---------
"""
@user.get('/api/v1/getData', tags=["Usuario"])
async def obtenerDatos():
    
    def is_empty(data_structure):
        if data_structure:
            return {
                "error": False,
                "message": "Datos existentes",
                "res": data
            }
        else:
            return {
                "error": False,
                "message": "No hay datos",
                "res": None
            }
    
    try:
        data = connection.execute(users.select()).fetchall()
        return is_empty(data) #Funcion para validar el diccionario 'data'
    except:
        return {
            "error": True,
            "message": "Internal error server: la peticion no se pudo procesar",
            "res": None
        }
"""

#--------- ruta: OBTENER USUARIO --------
@user.post('/api/v1/getUser', status_code=200, tags=['Usuario'])
async def obtenerUsuario(user: UserObtener):

    def is_empty(data_structure):
        if data_structure:
            return {
                "error": False,
                "message": "Usuario existente",
                "res": response
            }   
        else:
            return {
                "error": False,
                "message": "Usuario no existente",
                "res": None
            }
    
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text

    userArray= {"appConnect": appConnect, "keyUser": keyUser}

    if verificarVacio(userArray) == False:
        
        #Qsql= text("SELECT userID FROM keys WHERE appConnect=:appConnect OR key=:keyUser")
        #verRegistro= connection.execute(Qsql, appConnect=appConnect, key=keyUser).first()

        response= connection.execute(keys.select().where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()

        return is_empty(response)
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None
        }

#********* ruta: REGISTRAR USUARIO *********
@user.post('/api/v1/register', status_code=200, tags=['Usuario'])
async def registrar(user: UserRegistro):

    #Validando email: expresiones regulares
    def es_correo_valido(correo):
        expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        return re.match(expresion_regular, correo) is not None
        
    #Obtenemos el correo introducido por el usuario y lo pasa por validador de Email
    username= user.username.strip()
    username= BeautifulSoup(username, features='html.parser').text

    name= user.name.strip()
    name= BeautifulSoup(name, features='html.parser').text

    password= user.password.strip()
    password= BeautifulSoup(password, features='html.parser').text
    passw= base64.b64encode(password.encode("utf-8"))

    correo= user.email.strip()
    correo= BeautifulSoup(correo, features='html.parser').text

    #Creamos un diccionario con los valores del usuario,
    newUser = {"username": username, "name": name, "email": correo, "password": passw}

    if verificarVacio(newUser) == False:
        #Empezamos a procesar los datos
        if es_correo_valido(correo) == True:
            
            #Verificamos si el email ya ha sido registrado
            Qsql= text("SELECT email, username FROM users WHERE email=:email OR username=:username")
            verRegistro= connection.execute(Qsql, email=correo.strip(), username=username.strip()).first()

                    
            if verRegistro == None:

                #Generador de token/keyUser
                payload= datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                secreto= secrets.token_hex(10) + payload
                token= f.encrypt(secreto.encode("utf-8"))

                #Pasamos el token generado al campo keyUser
                newUser["keyUser"]= token 

                #Conexion a ApiLogin/users(tabla)/insertar valores de NEWUSER
                peticion= connection.execute(users.insert().values(newUser))
                return {
                    "error": False,
                    "message": "Usuario agregado correctamente.",
                    "res": None
                }
            else:
                return {
                    "error": True,
                    "message": "El usuario que intenta registrar ya existe.",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message": "Correo electronico invalido.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None
        }

#********* ruta: LOGIN *********
@user.post("/api/v1/login", status_code=200, tags=["Usuario"])
async def login(login: UserLogin):

    #Validando que la connection sea True
    def is_empty(con):
        if con:
            return {
                "error": False,
                "message": "Inicio de seccion correctamente",
                "res": {
                    "keyUser": token
                }
            }
        else:
            return {
                "error": False,
                "message": "Usuario no encontrado",
                "res": None
            }
    

    username= login.username.strip()
    username= BeautifulSoup(username, features='html.parser').text
        
    password= login.password.strip()
    password= BeautifulSoup(password, features='html.parser').text
    passw= base64.b64encode(password.encode("utf-8"))

    appConnect= login.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    #Recogemos los datos del usuario con el modelo 'UserLogin'
    dataLogin = {"username": username, "password": passw, "appConnect": appConnect}


    if verificarVacio(dataLogin) == False:

        #Peticiones a la base de datos para obtener y validar los datos ingresados por el usuario
        Qsql= text("SELECT userID FROM users WHERE password=:password AND username=:username")
        verLogin= connection.execute(Qsql, username=username, password=passw).first()

        #Verificamos con un if si el usuario ingresó correctamente sus credenciales
        if verLogin != None:

            #Almacenamos el userID del usuario en 'userIDK'
            userIDK= verLogin[0]

            #Generador de token/keyUser
            payload= datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            key = secrets.token_hex(20) + payload
            token= f.encrypt(key.encode("utf-8"))

            try:
                #keyApp= f.encrypt(payload.encode("utf-8"))
                dataLogin["keyUser"]= token

                #Obtener el userID del usuario para validarlo con userID de la base de datos.
                #Qsql= text("SELECT key FROM keys INNER JOIN users ON users.userID == keys=:userIDK")
                #verKey= connection.execute(Qsql, userIDK=userIDK).first()

                conx= connection.execute(keys.insert().values(keyUser= token, appConnect= appConnect, userID=userIDK))

                return is_empty(conx)
            except:
                return {
                    "error": True,
                    "message":"No se pudo ejecutar la peticion.",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message": "Username y/o Password inválido/s",
                "res": None
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None
        }

"""
#********* ruta: ACTUALIZAR *********
@user.put("/api/v1/actualizar/{keyUser}", tags=["Usuario"])
def actualizar(user: UserRequestModel, keyUser: str):

    #loginKey= {"keyUser": UserUpdate.keyUser}
    key = connection.execute(users.select().where(users.c.keyUser == keyUser)).first()

    def is_empty(data_structure):
        if data_structure:
            return {
                "error": False,
                "message": "Datos actualizados",
                "res": update
            }
        else:
            return {
                "error": True,
                "message": "Los datos no se pudieron actualizar",
                "res": None
            }
    
    #Empezamos a recibir y enviar datos a la base de datos
    try:

        if key:
        
            username= user.username
            password= user.password
            name= user.name
            email= user.email
            phone= user.phone
            dateOfBirth= user.dateOfBirth
            language= user.language
            country= user.country
            ypwCashBalance= user.ypwCashBalance
            shippingAddress= user.shippingAddress 
            identificationCard= user.identificationCard
            accountVersion= user.accountVersion
            timeZone= user.timeZone
            recoveryCode= user.recoveryCode
            applications= user.applications
            limitations= user.limitations
            accountType= user.accountType
            tradingExits= user.tradingExits
            pendingInvoices= user.pendingInvoices
            bills= user.bills
            subscriptions= user.subscriptions
            metodoPago= user.metodoPago
            servidorDB= user.servidorDB
            userDB= user.userDB
            puertoDB= user.puertoDB
            pagWeb= user.pagWeb

            update= {"username": username, "password": password, "name": name, "email": email, "phone": phone, 
            "dateOfBirth": dateOfBirth, "language": language, 
            "country": country, "ypwCashBalance": ypwCashBalance, 
            "shippingAddress": shippingAddress, "identificationCard": identificationCard, 
            "accountVersion": accountVersion, "timeZone": timeZone, 
            "recoveryCode": recoveryCode, "applications": applications, 
            "limitations": limitations, "accountType": accountType, 
            "tradingExits": tradingExits, "pendingInvoices": pendingInvoices, 
            "bills": bills, "subscriptions": subscriptions, 
            "metodoPago": metodoPago, "servidorDB": servidorDB, 
            "userDB": userDB, "puertoDB": puertoDB, "pagWeb": pagWeb}

            conx= connection.execute(users.update().values(update).where(users.c.keyUser == keyUser))

            return is_empty(conx)
        else:
            return {
                "error": True,
                "message": "keyUser inválido: usuario no encontrado.",
                "res": None
            }
    except:
        return {
            "error": True,
            "message": "La peticion no pudo ser procesada.",
            "res": None
        }
"""

#********* ruta: ELIMINAR *********
"""
@user.delete("/api/v1/delete/{keyUser}", tags=["Usuario"])
def eliminar(keyUser: str):

    def is_empty(data_structure):
        if data_structure:
            return {
                "error": False,
                "message": "Usuario eliminado exitosamente",
                "res": None
            }
        else:
            return {
                "error": False,
                "message": "El usuario no se pudo eliminar",
                "res": None
            }

    try:
        sql = connection.execute(users.delete().where(users.c.keyUser == keyUser))

        if sql:
            return is_empty(sql)
        else:
            return {
                "error": True,
                "message": "keyUser inválido: usuario no encontrado.",
                "res": None 
            }
    except:
        return {
            "error": True,
            "message": "La peticion no pudo ser procesada.",
            "res": None
        }
"""