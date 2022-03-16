import email
from email.policy import default
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

    #Y comprobamos si los inputs estan vacios
    def empty(data_structure):
        return all(not d for d in data_structure)
        #return len(data_structure) == 0

    #Obetenemos el correo introducido por el usuario y lo pasa por validador de Email
    username= user.username.lstrip()
    username= BeautifulSoup(username, features='html.parser').text
    #username= empty(username)

    name= user.name.lstrip()
    name= BeautifulSoup(name, features='html.parser').text
    #name= empty(name)

    password= user.password.lstrip()
    password= BeautifulSoup(password, features='html.parser').text
    #password= empty(password)

    correo= user.email.lstrip()
    correo= BeautifulSoup(correo, features='html.parser').text
    #correo= empty(correo)

    #Creamos un diccionario con los valores del usuario,
    newUser = {"username": username, "name": name, "email": correo, "password": password}


    if empty(newUser) == False:

        # Empezamos a procesar los datos
        if es_correo_valido(correo) == True:

            try:
                fecha = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
                newUser["registrationDate"] = fecha

                #Generador de token/keyUser
                name = newUser["name"]
                secreto = newUser['email'] + newUser['password']
                
                token = jwt.encode(
                    {"key":f"keyUser para {name}"},
                    secreto,
                    algorithm='HS256'
                )
                #res = jwt.decode(token, secreto, algorithms='HS256')
                #Pasamos el token generado al campo keyUser
                newUser["keyUser"] = token

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
            "message": "Existen espacios o campos vacios.",
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
                "res": token
            }
        else:
            return {
                "error": False,
                "message": "Usuario no encontrado",
                "res": None
            }

    try:
        #Recogemos los datos del usuario con el modelo 'UserLogin'
        dataLogin = {"username": login.username, "keyUser": login.keyUser}

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
            conx = connection.execute(users.update().values(token).where(users.c.keyUser == llave))
            #print(token)

            return is_empty(conx)
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
    #key = connection.execute(users.select().where(users.c.keyUser == u.keyUser)).first()

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

    try:
        
        update= {"username": user.username, "password": user.password,
        "name": user.name, "email": user.email, "phone": user.phone, 
        "dateOfBirth": user.dateOfBirth, "language": user.language, 
        "country": user.country, "ypwCashBalance": user.ypwCashBalance, 
        "shippingAddress": user.shippingAddress,  
        "identificationCard": user.identificationCard, 
        "accountVersion": user.accountVersion, 
        "timeZone": user.timeZone, 
        "recoveryCode": user.recoveryCode, "applications": user.applications, 
        "limitations": user.limitations, "accountType": user.accountType, 
        "tradingExits": user.tradingExits, "pendingInvoices": user.pendingInvoices, 
        "bills": user.bills, "subscriptions": user.subscriptions, 
        "metodoPago": user.metodoPago, "servidorDB": user.servidorDB, 
        "userDB": user.userDB, "puertoDB": user.puertoDB,
        "pagWeb": user.pagWeb}

        fecha = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        update["accountUpdateDate"]= fecha

        #localZone = datetime.timezone(datetime.timedelta(seconds=-time.timezone))
        #update["timeZone"]= localZone

        conx = connection.execute(users.update().values(update).where(users.c.keyUser == keyUser))

        return is_empty(conx)
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
        return is_empty(sql)
    except:
        return {
            "error": True,
            "message": "La peticion no pudo ser procesada.",
            "res": None
        }
    

#>> Generamos la fecha para introducirla en el modelo 'UserRegistro'
#fecha = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
