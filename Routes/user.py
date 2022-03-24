from pickle import NONE
from typing import Optional
import jwt, re, secrets
from fastapi import APIRouter
from bs4 import BeautifulSoup
from Database.conexion import conn as connection
from Models.index import users
from Schemas.schemas import UserLogin, UserRegistro, UserRequestModel
from fastapi.responses import JSONResponse
from datetime import datetime

user = APIRouter()


#--------- ruta: root ---------
@user.get('/', tags=["Welcome"])
async def root():
    return {"message": "Bienvenidos a APILogin YPW"}


#Y comprobamos si los inputs estan vacios
def verificarVacio(x):
    for i in x.values():
        if len(i) == 0:
            print(">> Vacio")
            return True
        else:
            print(">> No vacio")
            return False


#--------- ruta: OBTENER DATOS ---------
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


#--------- ruta: OBTENER USUARIO --------
@user.get('/api/v1/getUser/{userID}', tags=['Usuario'])
async def obtenerUsuario(userID: int):

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

    try:
        response = connection.execute(users.select().where(users.c.userID == userID)).first()
        return is_empty(response)
    except:
        return {
            "error": True,
            "message": "Internal error server: ha ocurrido un problema con la peticion",
            "res": None
        }


#********* ruta: REGISTRAR USUARIO *********
@user.post('/api/v1/register', tags=['Usuario'])
async def registrar(user: UserRegistro):

    #Validando email: expresiones regulares
    def es_correo_valido(correo):
        expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
        return re.match(expresion_regular, correo) is not None

    #Validando que la connection sea True
    def is_empty(data_structure, salida, error):
        if data_structure:
            return salida
        else:
            return error

    #Obetenemos el correo introducido por el usuario y lo pasa por validador de Email
    username= user.username.strip()
    username= BeautifulSoup(username, features='html.parser').text

    name= user.name.strip()
    name= BeautifulSoup(name, features='html.parser').text

    password= user.password.strip()
    password= BeautifulSoup(password, features='html.parser').text

    correo= user.email.strip()
    correo= BeautifulSoup(correo, features='html.parser').text

    #Creamos un diccionario con los valores del usuario,
    newUser = {"username": username, "name": name, "email": correo, "password": password}
    

    if verificarVacio(newUser) == False:
        #Empezamos a procesar los datos
        if es_correo_valido(correo) == True:

            try:
                #fecha = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
                newUser["registrationDate"]= None
                #Generador de token/keyUser
                name = newUser["name"]
                secreto = secrets.token_hex(10)
                
                token = jwt.encode(
                    {"key":f"keyUser para {name}"},
                    secreto,
                    algorithm='HS256'
                )
                #res = jwt.decode(token, secreto, algorithms='HS256')
                newUser["keyUser"]= token #Pasamos el token generado al campo keyUser

                #Conexion a ApiLogin/users(tabla)/insertar valores de NEWUSER
                peticion = connection.execute(users.insert().values(newUser))

                salida= {
                    "error": False,
                    "message": "Usuario agregado correctamente",
                    "res": {
                        "name": name,
                        "keyUser": token
                    }
                }

                error= {
                    "error": False,
                    "message": "Usuario no se pudo agregar",
                    "res": None
                }
                return is_empty(peticion, salida, error)
            except:
                return {
                    "error": True,
                    "message": "Ocurrió un problema en la peticion.",
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
@user.post("/api/v1/login", tags=["Usuario"])
async def login(login: UserLogin):

    #Validando que la connection sea True
    def is_empty(con):
        if con:
            return {
                "error": False,
                "message": "Usuario encontrado",
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

    try:
        username= login.username.strip()
        username= BeautifulSoup(username, features='html.parser').text
        
        keyUser= login.keyUser.strip()
        keyUser= BeautifulSoup(keyUser, features='html.parser').text

        #Recogemos los datos del usuario con el modelo 'UserLogin'
        dataLogin = {"username": username, "keyUser": keyUser}

        if verificarVacio(dataLogin) == False:

            #Peticiones a la base de datos para obtener y validar los datos ingresados por el usuario
            llave = connection.execute(users.select().where(users.c.keyUser == login.keyUser)).first()
            uName = connection.execute(users.select().where(users.c.username == login.username)).first()

            #Verificamos con un if si el usuario ingreso correctamente sus credenciales
            if llave and uName:

                #Generador de token/keyUser
                payload = dataLogin["username"]
                key = secrets.token_hex(10)

                token = jwt.encode(
                    {"key":f"keyUser para {payload}"},
                    key,
                    algorithm='HS256'
                )
                #keyDecodificada = jwt.decode(token, key, algorithms='HS256')
                #dataLogin["keyUser"]= token
                #token= dataLogin["keyUser"]

                conx = connection.execute(users.update().values(token).where(users.c.keyUser == llave))

                return is_empty(conx)
            else:
                return {
                    "error": True,
                    "message": "Username o Password inválido/s",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message": "Existen campos vacios.",
                "res": None
            }
    except:
        return {
            "error": True,
            "message": "Internal error server: no se pudo procesar la peticion.",
            "res": None
        }


#********* ruta: ACTUALIZAR *********
@user.put("/api/v1/actualizar/{keyUser}", tags=["Usuario"])
async def actualizar(user: UserRequestModel, keyUser: str):

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
            "shippingAddress": shippingAddress,  
            "identificationCard": identificationCard,
            "accountUpdateDate": "",
            "accountVersion": accountVersion, 
            "timeZone": timeZone, 
            "recoveryCode": recoveryCode, "applications": applications, 
            "limitations": limitations, "accountType": accountType, 
            "tradingExits": tradingExits, "pendingInvoices": pendingInvoices, 
            "bills": bills, "subscriptions": subscriptions, 
            "metodoPago": metodoPago, "servidorDB": servidorDB, 
            "userDB": userDB, "puertoDB": puertoDB,
            "pagWeb": pagWeb}

            #update["accountUpdateDate"]= ""

            #localZone = datetime.timezone(datetime.timedelta(seconds=-time.timezone))
            #update["timeZone"]= localZone
            conx = connection.execute(users.update().values(update).where(users.c.keyUser == keyUser))

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


#********* ruta: ELIMINAR *********
@user.delete("/api/v1/delete/{keyUser}", tags=["Usuario"])
async def eliminar(keyUser: str):

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
    