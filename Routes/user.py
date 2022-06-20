import re, secrets, bcrypt, base64, hashlib, random
from fastapi import APIRouter
from bs4 import BeautifulSoup
from sqlalchemy import text
from Models.index import users, keys
from Schemas.schemas import UserLogin, UserObtener, UserRegistro, UserLogout, UserSeccion, ChangePassw, SetCode, RecoveryPassCode
from config.email import enviarEmail
from datetime import datetime
from cryptography.fernet import Fernet
from Database.conexion import engine

user = APIRouter()


#-------- Eventos para validar conexion a DB () --------
@user.on_event("startup")
async def startup():
    print("Application startup")

@user.on_event("shutdown")
async def shutdown():
    print("Application shutdown")


#--------- ruta: root ---------
@user.get('/', tags=["Welcome"])
async def root():
    return {
        "error": False,
        "message": "Bienvenid@ a APILogin YPW",
        "res": None
    }


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


#FUNCION PARA ENCRIPTAR EL PASSWORD DE USUARIO
def encrytPassw(passw):

    with open('./config/secretKey.txt') as file:
        secretKey= file.read()
        secretKey= bytes(secretKey, encoding='ascii')
        file.close()

    key = bcrypt.kdf(
        password= passw,
        salt= secretKey,
        desired_key_bytes= 64,
        rounds= 100
    )

    passwd= base64.b64encode(hashlib.sha256(key).digest())
    return passwd



#VALIDANDO EMAIL: expresiones regulares
def es_correo_valido(correo):
    expresion_regular = r"(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, correo) is not None

#VALIDANDO PHONE: expresiones regulares
def es_telefono_valido(phone):
    expresion_regular = r"^[+]?(\d{1,4})?\s?-?[.]?[(]?\d{3}[)]?\s?-?[.]?\d{3}\s?-?[.]?\d{4}$"
    return re.match(expresion_regular, phone) is not None


#Generador de token/keyUser.
def generarToken():
    payload= datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    key = secrets.token_hex(20) + payload
    token= f.encrypt(key.encode("utf-8"))
    return token

def generarCode():
    codetmp= random.randint(100000, 999999)
    return codetmp

#FUNCION PARA AUTOLOGIN AL REGISTRARSE
def autoLogin(email, passw):
    arg= (email, passw,)
    
    try:
        with engine.connect() as conn:
            cursor= conn.connection.cursor()
            cursor.callproc('loginEmail', args=arg)
            conn.connection.commit()
            output= cursor.fetchone()
            userID= output[0]
    finally:
        conn.close()
    return userID



#--------- ruta: OBTENER USUARIO --------
@user.post('/api/v1/account/getUser', status_code=200, tags=['Usuario'])
async def obtenerUsuario(user: UserObtener):
    
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text

    #Creamos un diccionario con los valores del usuario
    userArray= {"appConnect": appConnect, "keyUser": keyUser}
    
    #Verificamos si algun campo esta vacio
    if verificarVacio(userArray) == False:
        
        try:
            #Consultamos a la base de datos para obtener el userID del usuario
            with engine.connect() as conn:
                verDatos= conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        #Verificamos si ha capturado datos.
        if verDatos != None:

            #Almacenamos en userID el userID del usuario
            userID= verDatos[0]
            
            try:
                #Comprobamos si el userID de las tablas hacen match para obtener todos los datos del usuario
                with engine.connect() as conn:
                    response= conn.execute(users.select().where(users.c.userID == userID)).first()
            finally:
                conn.close()
            
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
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None
        }


#********* ruta: REGISTRAR USUARIO *********
@user.post('/api/v1/account/register', status_code=200, tags=['Usuario'])
async def registrar(user: UserRegistro):
        
    #Obtenemos el correo introducido por el usuario y lo pasa por validador de Email
    username= user.username.strip()
    username= BeautifulSoup(username, features='html.parser').text

    name= user.name.strip()
    name= BeautifulSoup(name, features='html.parser').text

    password= user.password.strip()
    password= BeautifulSoup(password, features='html.parser').text
    passw= password.encode()
    passw= encrytPassw(passw)

    email= user.email.strip()
    email= BeautifulSoup(email, features='html.parser').text
    
    phone= user.phone.strip()
    phone= BeautifulSoup(phone, features='html.parser').text

    #Creamos un diccionario con los valores del usuario
    newUser = {"username": username, "password": passw, "email": email, "name": name, "phone": phone}

    if verificarVacio(newUser) == False:
        #Empezamos a procesar el correo electronico
        if es_correo_valido(email) == True:
            #Empezamos a procesar el numero de telefono
            if es_telefono_valido(phone) == True:
                
                #Elimina los caracteres del phone
                phone= re.sub("\!|\'|\?|\ |\(|\)|\-|\+","", phone)
                
                try:
                    #Usamos el procedimiento almacenado para registrar el usuario y el token generado.
                    with engine.connect() as conn:
                        cursor= conn.connection.cursor()
                        arg= (username, passw, email, name, phone, 0)
                        cursor.callproc('registerUser', args=arg)
                        conn.connection.commit()
                        output= cursor.fetchone()
                        output= output[0]
                finally:
                    conn.close()
                
                if output == 1:
                    
                    token= generarToken()
                    login= autoLogin(email, passw)
                    
                    try:
                        with engine.connect() as conn:
                            conn.execute(keys.insert().values(keyUser= token, appConnect="default", userID=login))
                    finally:
                        conn.close()
                    
                    return {
                        "error": False,
                        "message": "Usuario agregado correctamente.",
                        "res": {
                            "appConnect": "default",
                            "keyUser": token
                        }
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
                    "message": "Número de teléfono inválido.",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message": "Correo electrónico inválido.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None
        }


#********* ruta: LOGIN *********
@user.post("/api/v1/account/login", status_code=200, tags=["Usuario"])
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
    
    #CAMPO: uceCampo: username, telefono, email
    username= login.username.strip()
    username= BeautifulSoup(username, features='html.parser').text
    
    password= login.password.strip()
    password= BeautifulSoup(password, features='html.parser').text
    passw= password.encode()
    passw= encrytPassw(passw)
    
    appConnect= login.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    dataLogin = {"username": username, "password": passw, "appConnect": appConnect}
    
    #Comprueba los campos y ejecuta las conexiones
    if verificarVacio(dataLogin) == False: 
        
        if es_correo_valido(username) == True:
            
            try:
                #Usando procedimiento almacenado: loginEmail
                with engine.connect() as conn:
                    cursor= conn.connection.cursor()
                    arg= (username, passw,)
                    cursor.callproc('loginEmail', args=arg)
                    conn.connection.commit()
                    output= cursor.fetchone()
            finally:
                conn.close()
                
        elif es_telefono_valido(username) == True:
            username= re.sub("\!|\'|\?|\ |\(|\)|\-|\+","", username)
            
            try:
                #Usando procedimiento almacenado: loginPhone
                with engine.connect() as conn:
                    cursor= conn.connection.cursor()
                    arg= (username, passw,)
                    cursor.callproc('loginPhone', args=arg)
                    conn.connection.commit()
                    output= cursor.fetchone()
            finally:
                conn.close()
        else:
            try:
                #Usando procedimiento almacenado: loginUser
                with engine.connect() as conn:
                    cursor= conn.connection.cursor()
                    arg= (username, passw,)
                    cursor.callproc('loginUser', args=arg)
                    conn.connection.commit()
                    output= cursor.fetchone()
            finally:
                conn.close()


        if output != None:
            #Almacenamos el userID del usuario en 'userIDK'
            output= output[0]
        
            #Generador de token/keyUser
            token= generarToken()

            try:
                dataLogin["keyUser"]= token
                
                try:
                    with engine.connect() as conn:
                        conx= conn.execute(keys.insert().values(keyUser= token, appConnect= appConnect, userID=output))
                finally:
                    conn.close()

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


#********* ruta: CERRAR SECCION *********
@user.post('/api/v1/account/logout', status_code=200, tags=['Usuario'])
async def logout(user: UserLogout):
    
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text

    #Creamos un diccionario con los valores del usuario
    userArray= {"appConnect": appConnect, "keyUser": keyUser}

    #Verificamos si algun campo esta vacio
    if verificarVacio(userArray) == False:
        
        try:
            #Consultamos a la base de datos para obtener el userID del usuario
            with engine.connect() as conn:
                verSeccion= conn.execute(keys.select().where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        #Verificamos si ha capturado datos.
        if verSeccion != None:
            
            try:
                #Consultamos a la base de datos para eliminar el usuario
                with engine.connect() as conn:
                    conn.execute(keys.delete().where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect))
            finally:
                conn.close()
        
            return {
                "error": False,
                "message": "Seccion cerrada correctamente.",
                "res": None
            }
        else:
            return {
               "error": True,
                "message": "La seccion no existe.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None
        }


#********* ruta: OBTENER TODAS LAS APPS DEL USUARIO *********
@user.post('/api/v1/account/getSections', status_code=200, tags=['Usuario'])
async def getSections(user: UserSeccion):

    #Validando que la connection sea True
    def is_empty(con):
        if con:
            return {
                "error": False,
                "message": "Apps conectadas a ypwLogin",
                "res": conx
            }
        else:
            return {
                "error": False,
                "message": "No existen apps conectadas a este usuario.",
                "res": None
            }
    
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text

    #Creamos un diccionario con los valores del usuario
    userArray= {"appConnect": appConnect, "keyUser": keyUser}

    if verificarVacio(userArray) == False:
        
        try:
            #Peticiones a la base de datos para obtener y validar los datos ingresados por el usuario.
            with engine.connect() as conn:
                login= conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()
        
        #Verificamos con un if si el usuario ingresó correctamente sus credenciales.
        if login != None:
            
            try:
                #Almacenamos el userID del usuario en 'userIDU'
                userIDU= login[0]
                
                try:
                    with engine.connect() as conn:
                        conx= conn.execute(keys.select().where(keys.c.userID == userIDU)).fetchall()
                finally:
                    conn.close()

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
                "message": "keyUser y/o appConnect inválido/s",
                "res": None
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None
        }


#********* ruta: CAMBIAR CONTRASEÑA DEL USUARIO *********
@user.post('/api/v1/account/changePassword', status_code=200, tags=['Usuario'])
async def changePassword(user: ChangePassw):
            
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    newPassword= user.newPassword.strip()
    newPassword= BeautifulSoup(newPassword, features='html.parser').text
    newPassw= newPassword.encode()
    newPassw= encrytPassw(newPassw)
    
    removeSections= user.removeSections

    #Creamos un diccionario con los valores del usuario
    userArray= {"appConnect": appConnect, "keyUser": keyUser, "newPassword": newPassw}

    #Verificamos si algun campo esta vacio
    if verificarVacio(userArray) == False:
        
        try:
            #Consultamos a la base de datos para obtener el userID del usuario
            with engine.connect() as conn:
                vlogin= conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()
        
        #Verificamos si ha capturado datos.
        if vlogin != None:
            
            userIDU= vlogin[0]
            
            try:
                with engine.connect() as conn:
                    conn.execute(users.update().values(password= newPassw).where(users.c.userID == userIDU))
            finally:
                conn.close()
            
            if removeSections == True:
                try:
                    with engine.connect() as conn:
                        conn.execute(keys.delete().where(keys.c.userID == userIDU))
                finally:
                    conn.close()
                
                return {
                    "error": False,
                    "message": {
                        "m1:": "La contraseña ha sido actualizada exitosamente.",
                        "m2:": "Todas las secciones se han eliminado."
                    },
                    "res": None
                }
            else:
                return {
                    "error": False,
                    "message": "La contraseña ha sido actualizada exitosamente.",
                    "res": None
                }
        else:
            return {
               "error": True,
                "message": "Username y/o Password inválido/s.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None
        }

#--------- ruta: ENVIO DE CODIGO A EMAIL --------
@user.post('/api/v1/account/setCode', status_code=200, tags=['Usuario'])
async def enviarPassCode(user: SetCode):
    
    email= user.email.strip()
    email= BeautifulSoup(email, features='html.parser').text
    
    dataRecovery= {"email": email}
    
    #Comprueba los campos y ejecuta las conexiones
    if verificarVacio(dataRecovery) == False: 
        
        if es_correo_valido(email) == True:
            
            try:
                with engine.connect() as conn:
                    sql= text("select email from users where email=:email")
                    output= conn.execute(sql, email=email).first()
            finally:
                conn.close()
            
            if output != None:
                
                #Generando codigo de verificacion
                codeTMP= generarCode()
                
                try:
                    with engine.connect() as conn:
                        conn.execute(users.update().values(codetmp=codeTMP).where(users.c.email == email))
                finally:
                    conn.close()
                
                if enviarEmail(email, codeTMP) == None:
                    
                    return {
                        "error": False,
                        "message": "Correo enviado exitosamente.",
                        "res": None
                    }
                else:
                    return {
                        "error": False,
                        "message": "Correo no se pudo enviar.",
                        "res": None
                    }
            else:
                return {
                    "error": True,
                    "message": "Correo electrónico no encontrado.",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message":"Correo electrónico inválido.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None
        }

#--------- ruta: OBTENER USUARIO --------
@user.post('/api/v1/account/changePasswCode', status_code=200, tags=['Usuario'])
async def cambiarPassCode(user: RecoveryPassCode):
    
    email= user.email.strip()
    email= BeautifulSoup(email, features='html.parser').text
    
    codetmp= user.codetmp.strip()
    codetmp= BeautifulSoup(codetmp, features='html.parser').text
    
    newPassword= user.newPassword.strip()
    newPassword= BeautifulSoup(newPassword, features='html.parser').text
    newPassw= newPassword.encode()
    newPassw= encrytPassw(newPassw)
    
    dataRecovery= {"email": email, "codetmp": codetmp, "newPassword": newPassw}
    
    #Comprueba los campos y ejecuta las conexiones
    if verificarVacio(dataRecovery) == False: 
        
        if es_correo_valido(email) == True:
            
            try:
                with engine.connect() as conn:
                    sql= text("select * from users where email=:email and codetmp=:codetmp")
                    output= conn.execute(sql, email=email, codetmp=codetmp).first()
            finally:
                conn.close()
            
            
            if output != None:
                
                try:
                    with engine.connect() as conn:
                        conn.execute(users.update().values(password= newPassw, codetmp=None).where(users.c.codetmp == codetmp, users.c.email == email))
                finally:
                    conn.close()
                
                return {
                    "error": False,
                    "message":"Contraseña ha sido restablecida exitosamente.",
                    "res": None
                }
            else:
                return {
                    "error": True,
                    "message": "Correo electrónico y/o Password inválido/s",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message":"Correo electrónico inválido.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None
        }


"""
#********* ruta: ACTUALIZAR *********
@user.put("/api/v1/account/actualizar/{keyUser", tags=["Usuario"])
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