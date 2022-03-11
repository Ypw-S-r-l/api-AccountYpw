from wsgiref import headers
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
import jwt, re, secrets
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
            "message": "La peticion no se pudo procesar",
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
            "message": "Ha ocurrido un problema con la peticion",
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
    def is_empty(data_structure):
        if data_structure:
            return {
                "error": False,
                "message": "Usuario agregado correctamente",
                "res": {
                    "name": name,
                    "keyUser": token
                }
            }
        else:
            return {
                "error": False,
                "message": "Usuario no se pudo agregar",
                "res": None
            }

    #Obetenemos el correo introducido por el usuario y lo pasa por validador de Email
    correo = user.email
    correo.format(correo, es_correo_valido(correo))

    if es_correo_valido(correo) == True:

        try:
            #Campos a rellenar
            newUser = {"username": user.username, "name": user.name, "email": correo, "password": user.password}

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
            return is_empty(peticion)
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


#********* ruta: LOGIN *********
@user.post("/api/v1/login", tags=["Usuario"])
async def login(login: UserLogin):

    try:
        #Recogemos los datos del usuario con el modelo 'UserLogin'
        dataLogin = {"username": login.username, "keyUser": login.keyUser}

        #Peticiones a la base de datos para obtener y validar los datos ingresados por el usuario
        llave = connection.execute(users.select().where(users.c.keyUser == login.keyUser)).first()
        uName = connection.execute(users.select().where(users.c.username == login.username)).first()

        #Verificamos con un if si el usuario ingreso correctamente sus credenciales
        if llave and uName:

            #Obtenemos el keyUser del usuario
            #kUser = dataLogin["username"]

            #Generador de token/keyUser
            payload = dataLogin["username"]
            key = secrets.token_hex(10)

            token = jwt.encode(
                {"key":f"keyUser para {payload}"},
                key,
                algorithm='HS256'
            )
            keyDecodificada = jwt.decode(token, key, algorithms='HS256')
            connection.execute(users.update().values(token).where(users.c.username == payload))
            print(token)

            return JSONResponse(
                status_code=200, 
                content= {
                    "error": False,
                    "message": "Usuario encontrado",
                    "res": token
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content= {
                    "error": True,
                    "message": "Usuario no encontrado",
                    "res": None
                }
            )
    except:
        return JSONResponse(
            status_code= 500,
            content= {
                "error": True,
                "message": "No se pudo procesar la peticion.",
                "res": None
            }
        )


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
                "error": False,
                "message": "Los datos no se pudieron actualizar",
                "res": None
            }

#rosalbasuarez530luis
#rosalbas53

#luisgabriel530luis
#luissg53

    try:
        
        update= {"username": user.username, "password": user.password,
        "name": user.name, "email": user.email, "phone": user.phone, 
        "dateOfBirth": user.dateOfBirth, "language": user.language, 
        "country": user.country, "ypwCashBalance": user.ypwCashBalance, 
        "shippingAddress": user.shippingAddress, 
        "registrationDate": user.registrationDate, 
        "identificationCard": user.identificationCard, 
        "accountVersion": user.accountVersion, "timeZone": user.timeZone, 
        "recoveryCode": user.recoveryCode, "applications": user.applications, 
        "limitations": user.limitations, "accountType": user.accountType, 
        "tradingExits": user.tradingExits, "pendingInvoices": user.pendingInvoices, 
        "bills": user.bills, "subscriptions": user.subscriptions, 
        "metodoPago": user.metodoPago, "servidorDB": user.servidorDB, 
        "userDB": user.userDB, "puertoDB": user.puertoDB,
        "pagWeb": user.pagWeb}


        """
        update= connection.execute(users.update().values(
            username= user.username, password= user.password, 
            name= user.name, email= user.email, phone= user.phone, dateOfBirth= user.dateOfBirth, 
            language= user.language, country= user.country, ypwCashBalance= user.ypwCashBalance, 
            shippingAddress= user.shippingAddress, identificationCard= user.identificationCard, 
            registrationDate= user.registrationDate, accountUpdateDate= user.accountUpdateDate, 
            accountVersion= user.accountVersion, timeZone= user.timeZone, recoveryCode= user.recoveryCode, 
            applications= user.applications, limitations= user.limitations, accountType= user.accountType, 
            tradingExits= user.tradingExits, pendingInvoices= user.pendingInvoices, bills= user.bills, 
            subscriptions= user.subscriptions, metodoPago= user.metodoPago, servidorDB= user.servidorDB, 
            userDB= user.userDB, puertoDB= user.puertoDB, pagWeb= user.pagWeb
        ).where(users.c.keyUser == keyUser))
        """

        fecha = datetime.today().strftime('%d-%m-%Y %H:%M:%S')
        update["accountUpdateDate"] = fecha

        conx = connection.execute(users.update().values(update).where(users.c.keyUser == keyUser))

        return conx
    except:
        return {
            "error": True,
            "message": "La peticion no pudo ser procesada.",
            "res": None
        }


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
