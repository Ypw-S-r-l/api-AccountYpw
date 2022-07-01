import re, secrets, bcrypt, base64, hashlib, random, warnings
from starlette.status import *
from fastapi import APIRouter, Response
from bs4 import BeautifulSoup
from sqlalchemy import text
from Models.index import users, keys
from Schemas.schemas import UserLogin, UserObtener, UserRegistro, UserUpdate, UserUpdateOpcional, UserLogout, UserSeccion, ChangePassw, SetCode, RecoveryPassCode, UpdateFieldData
from config.email import enviarEmail
from datetime import datetime
from cryptography.fernet import Fernet
from Database.conexion import engine
from config.methods import APIversion

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
        "res": None,
        "version": APIversion()
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
                "res": response,
                "version": APIversion()
            }
        else:
            return {
               "error": False,
                "message": "Usuario no existente",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
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
                        },
                        "version": APIversion()
                    }
                else:
                    return {
                        "error": True,
                        "message": "El usuario que intenta registrar ya existe.",
                        "res": None,
                        "version": APIversion()
                    }
            else:
                return {
                    "error": True,
                    "message": "Número de teléfono inválido.",
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
                "error": True,
                "message": "Correo electrónico inválido.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None,
            "version": APIversion()
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
                },
                "version": APIversion()
            }
        else:
            return {
                "error": False,
                "message": "Usuario no encontrado",
                "res": None,
                "version": APIversion()
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
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
                "error": True,
                "message": "Username y/o Password inválido/s",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None,
            "version": APIversion()
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
                "res": None,
                "version": APIversion()
            }
        else:
            return {
               "error": True,
                "message": "La seccion no existe.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
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
                "res": conx,
                "version": APIversion()
            }
        else:
            return {
                "error": False,
                "message": "No existen apps conectadas a este usuario.",
                "res": None,
                "version": APIversion()
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
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
                "error": True,
                "message": "keyUser y/o appConnect inválido/s",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message": "Existen campos vacios.",
            "res": None,
            "version": APIversion()
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
                    "res": None,
                    "version": APIversion()
                }
            else:
                return {
                    "error": False,
                    "message": "La contraseña ha sido actualizada exitosamente.",
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
               "error": True,
                "message": "Username y/o Password inválido/s.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
        }

#--------- ruta: ENVIO DE CODIGO A EMAIL --------
@user.post('/api/v1/account/setCode/email', status_code=200, tags=['Usuario'])
async def enviarPassCodeEmail(user: SetCode):
    
    #>> Elimina fallas de la libreria: BeautifulSoup
    warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
    
    #>> Verificar el envio del cbodyorreo: capturando errores
    def verEnvioEmail(email, codeTMP, header, body, support, footer):
        if enviarEmail(email, codeTMP, header, body, support, footer) == None:
            return {
                "error": False,
                "message": "Correo enviado exitosamente.",
                "res": None,
                "version": APIversion()
            }
        else:
            return {
                "error": False,
                "message": "Correo no se pudo enviar.",
                "res": None,
                "version": APIversion()
            }
    
    email= user.email.strip()
    email= BeautifulSoup(email, features='html.parser').text
    
    header= user.header.strip()
    header= BeautifulSoup(header, features='html.parser').text
    
    body= user.body.strip()
    body= BeautifulSoup(body, features='html.parser').text
    
    support= user.support.strip()
    support= BeautifulSoup(support, features='html.parser').text
    
    footer= user.footer.strip()
    footer= BeautifulSoup(footer, features='html.parser').text
    
    dataRecovery= {"email": email}
    arrayEmail= {"header": header, "body": body, "support": support, "footer": footer}
    
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
                
                if verificarVacio(arrayEmail) == False:
                    return verEnvioEmail(email, codeTMP, header, body, support, footer)
                else:
                    header= "YPW"
                    body= "Su codigo de recuperacion es:"
                    support= "https://ypw.com.do/#about"
                    footer= "2022 © YPW S.R.L"
                    
                    return verEnvioEmail(email, codeTMP, header, body, support, footer)
            else:
                return {
                    "error": True,
                    "message": "Correo electrónico no encontrado.",
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
                "error": True,
                "message":"Correo electrónico inválido.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
        }

#--------- ruta: OBTENER USUARIO --------
@user.post('/api/v1/account/changePasswCode/email', status_code=200, tags=['Usuario'])
async def cambiarPassCodeEmail(user: RecoveryPassCode):
    
    email= user.email.strip()
    email= BeautifulSoup(email, features='html.parser').text
    
    codetmp= user.codetmpEmail.strip()
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
                    "res": None,
                    "version": APIversion()
                }
            else:
                return {
                    "error": True,
                    "message": "Correo electrónico y/o Password inválido/s",
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
                "error": True,
                "message":"Correo electrónico inválido.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
        }

"""
#********* ruta: ACTUALIZAR *********
@user.patch("/api/v1/account/updateUser", status_code=200, response_model_exclude_unset=True, tags=["Usuario"])
async def actualizarUsuario(user: UserUpdate):
    
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    username= user.username
    username= str(username).strip()
    username= BeautifulSoup(username, features='html.parser').text

    name= user.name
    name= str(name).strip()
    name= BeautifulSoup(name, features='html.parser').text
    
    phone= user.phone
    phone= str(phone).strip()
    phone= BeautifulSoup(phone, features='html.parser').text

    #Creamos un diccionario con los valores del usuario
    array= {"keyUser": keyUser, "appConnect": appConnect}
    arrayUsername= {"username": username}
    arrayPhone= {"phone": phone}
    
    if verificarVacio(array) == False:
        #Consultamos a la base de datos para obtener el userID del usuario 
        try:
            with engine.connect() as conn:
                vlogin= conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()
        
        if vlogin != None:
            userID= vlogin[0]
            
            try:
                with engine.connect() as conn:
                    output= conn.execute(users.select().where(users.c.username == username)).first()
            finally:
                conn.close()
            
            if output == None:
                if es_telefono_valido(phone) == True:
                
                    #Elimina los caracteres del phone
                    phone= re.sub("\!|\'|\?|\ |\(|\)|\-|\+","", phone)
                    arrayUser= {"username": username, "name": name, "phone": phone}
                            
                    try:
                        with engine.connect() as conn:
                            conn.execute(users.update().values(username=username, name=name, phone=phone).where(users.c.userID == userID))
                    finally:
                            conn.close()
                    
                    return {
                        "error": False,
                        "message": "Datos han sido actualizados.",
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
                    "message": "Nombre de usuario no disponible",
                    "res": None
                }
        else:
            return {
                "error": True,
                "message": "No se encontró la seccion.",
                "res": None
            }
    else:
        return {
            "error": True,
            "message":"Campos obligatorios vacios.",
            "res": None
        }
"""

#********* ruta: ACTUALIZAR *********
@user.put("/api/v1/account/updateDataUser", status_code=200, response_model_exclude_unset=True, tags=["Usuario"])
async def actualizarDatos(user: UserUpdateOpcional):

    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    name= user.name.strip()
    name= BeautifulSoup(name, features='html.parser').text
    
    dateOfBirth= user.dateOfBirth
    dateOfBirth= str(dateOfBirth).strip()
    dateOfBirth= BeautifulSoup(dateOfBirth, features='html.parser').text
    
    language= user.language
    language= str(language).strip()
    language= BeautifulSoup(language, features='html.parser').text
    
    country= user.country
    country= str(country).strip()
    country= BeautifulSoup(country, features='html.parser').text
    
    shippingAddress= user.shippingAddress
    #shippingAddress= str(shippingAddress).strip()
    #shippingAddress= BeautifulSoup(shippingAddress, features='html.parser').text
    
    identificationCard= user.identificationCard
    identificationCard= str(identificationCard).strip()
    identificationCard= BeautifulSoup(identificationCard, features='html.parser').text

    accountVersion= user.accountVersion
    accountVersion= str(accountVersion).strip()
    accountVersion= BeautifulSoup(accountVersion, features='html.parser').text

    timeZone= user.timeZone
    timeZone= str(timeZone).strip()
    timeZone= BeautifulSoup(timeZone, features='html.parser').text
    
    accountType= user.accountType
    accountType= str(accountType).strip()
    accountType= BeautifulSoup(accountType, features='html.parser').text
    
    pagWeb= user.pagWeb
    pagWeb= str(pagWeb).strip()
    pagWeb= BeautifulSoup(pagWeb, features='html.parser').text
    
    array= {"keyUser": keyUser, "appConnect": appConnect}
    
    if verificarVacio(array) == False:
        #Consultamos a la base de datos para obtener el userID del usuario 
        try:
            with engine.connect() as conn:
                vlogin= conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()
        
        if vlogin != None:
            
            userID= vlogin[0]
            
            try:
                with engine.connect() as conn:
                    conn.execute(users.update().values(name=name, dateOfBirth=dateOfBirth, language=language, country=country, shippingAddress=shippingAddress, identificationCard=identificationCard, accountVersion=accountVersion, timeZone=timeZone, accountType=accountType, pagWeb=pagWeb).where(users.c.userID == userID))
            finally:
                conn.close()
            
            return {
                "error": False,
                "message": "Datos actualizados exitosamente.",
                "res": None,
                "version": APIversion()
            }
        else:
            return {
                "error": True,
                "message": "No se encontró la seccion.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
        }

#********* ruta: ACTUALIZAR *********
@user.put("/api/v1/account/updateFieldData", status_code=200, response_model_exclude_unset=True, tags=["Usuario"])
async def actualizarCampoData(user: UpdateFieldData):
    
    appConnect= user.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= user.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    data= user.data
    #data= str(data).strip()
    #data= BeautifulSoup(data, features='html.parser').text
    
    array= {"keyUser": keyUser, "appConnect": appConnect}
    
    if verificarVacio(array) == False:
        #Consultamos a la base de datos para obtener el userID del usuario 
        try:
            with engine.connect() as conn:
                vlogin= conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()
        
        if vlogin != None:
            userID= vlogin[0]
            
            if data:
                try:
                    with engine.connect() as conn:
                        conn.execute(users.update().values(data=data).where(users.c.userID == userID))
                finally:
                    conn.close()
                
                return {
                    "error": False,
                    "message": "Datos actualizados exitosamente.",
                    "res": None,
                    "version": APIversion()
                }
            else:
                return {
                    "error": True,
                    "message": "No se enviaron datos para actualizar.",
                    "res": None,
                    "version": APIversion()
                }
        else:
            return {
                "error": True,
                "message": "No se encontró la seccion.",
                "res": None,
                "version": APIversion()
            }
    else:
        return {
            "error": True,
            "message":"Existen campos vacios.",
            "res": None,
            "version": APIversion()
        }