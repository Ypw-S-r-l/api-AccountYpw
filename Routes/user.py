import re, secrets, bcrypt, base64, hashlib, random, warnings
from starlette.status import *
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from bs4 import BeautifulSoup
from sqlalchemy import text
from Models.index import users, keys
from Schemas.schemas import *
from datetime import datetime
from cryptography.fernet import Fernet
from Database.conexion import engine
from config.methods import *
from config.regexp import *
from config.authentication import security, get_current_username

user = APIRouter(prefix=f"/api/{version[0]}/account")

# --------- ruta: root ---------
@user.get('/', tags=["Welcome"])
async def root():
    return responseModelErrorX(status.HTTP_200_OK, False, "Bienvenid@ a APILogin YPW", None)

# Y comprobamos si los inputs estan vacios
def verificarVacio(x):
    for i in x.values():
        if len(i) == 0:
            return True
        else:
            return False


#>> Para generar keyUser
key = Fernet.generate_key()
f = Fernet(key)

#>> FUNCION PARA ENCRIPTAR EL PASSWORD DE USUARIO
def encrytPassw(passw):

    with open('./config/secretKey.txt') as file:
        secretKey = file.read()
        secretKey = bytes(secretKey, encoding='ascii')
        file.close()

    key = bcrypt.kdf(
        password=passw,
        salt=secretKey,
        desired_key_bytes=64,
        rounds=100
    )

    passwd = base64.b64encode(hashlib.sha256(key).digest())
    return passwd


# Generador de token/keyUser.
def generarToken():
    payload = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    key = secrets.token_hex(20) + payload
    token = f.encrypt(key.encode("utf-8"))
    return token

# Generador de codigo de 6 digitos.
def generarCode():
    codetmp = random.randint(100000, 999999)
    return codetmp

# --------- ruta: OBTENER USUARIO --------
@user.post('/getUser', status_code=200, response_model=UserObtener, tags=['Usuario'])
async def obtenerUsuario(user: UserObtener):

    appConnect = user.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    keyUser = user.keyUser.strip()
    keyUser = BeautifulSoup(keyUser, features='html.parser').text

    # Creamos un diccionario con los valores del usuario
    userArray = {"appConnect": appConnect, "keyUser": keyUser}

    # Verificamos si algun campo esta vacio
    if UserObtener:

        try:
            # Consultamos a la base de datos para obtener el userID del usuario
            with engine.connect() as conn:
                verDatos = conn.execute(keys.select(keys.c.userID).where(
                    keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        # Verificamos si ha capturado datos.
        if verDatos != None:
            # Almacenamos en userID el userID del usuario
            userID = verDatos[0]
            try:
                # Comprobamos si el userID de las tablas hacen match para obtener todos los datos del usuario
                with engine.connect() as conn:
                    response= conn.execute(users.select().where(users.c.userID == userID)).first()
                    
                    #sql= text("select userID, username, name, email, phone, dateOfBirth, language, country, ypwCashBalance, shippingAddress, registrationDate, identificationCard, accountUpdateDate, accountVersion, timeZone, recoveryCode, applications, limitations, accountType, tradingExits, pendingInvoices, bills, subscriptions, metodoPago, servidorDB, userDB, puertoDB, pagWeb, data, block, developer from users where userID=:userID")
                    #response= conn.execute(sql, userID=userID).first()
            finally:
                conn.close()

            return responseModelErrorX(status.HTTP_200_OK, False, "Usuario existente", response)
        else:
            return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no existente", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: REGISTRAR USUARIO *********
@user.post('/register', status_code=200, response_model=UserRegistro, tags=['Usuario'])
async def registrar(user: UserRegistro):

    # Obtenemos el correo introducido por el usuario y lo pasa por validador de Email
    username = user.username.strip()
    username = BeautifulSoup(username, features='html.parser').text

    name = user.name.strip()
    name = BeautifulSoup(name, features='html.parser').text

    password = user.password.strip()
    password = BeautifulSoup(password, features='html.parser').text

    email = user.email.strip()
    email = BeautifulSoup(email, features='html.parser').text
    
    numberCode = user.numberCode
    numberCode= str(numberCode).strip()
    numberCode = BeautifulSoup(numberCode, features='html.parser').text
    
    phone = user.phone.strip()
    phone = BeautifulSoup(phone, features='html.parser').text

    # Creamos un diccionario con los valores del usuario
    newUser = {"username": username, "password": password,
               "email": email, "name": name, "phone": phone}

    if verificarVacio(newUser) == False:
        # Empezamos a procesar el name
        if es_nombre_valido(name) == True:
            # Empezamos a procesar el username
            if es_usuario_valido(username) == True:
                # Empezamos a procesar el correo electronico
                if es_correo_valido(email) == True:
                    # Empezamos a procesar el numero de telefono
                    if es_telefono_valido(phone) == True:

                        # Elimina los caracteres del phone
                        phone = re.sub("\!|\'|\?|\ |\(|\)|\-|\+", "", phone)

                        if es_password_valido(password) == True:
                            # Encodea el password
                            passw = password.encode()
                            passw = encrytPassw(passw)
                            
                            #>> Generando codigo de activacion de cuenta
                            codeTMP = generarCode()

                            try:
                                # Usamos el procedimiento almacenado para registrar el usuario y el token generado.
                                with engine.connect() as conn:
                                    cursor = conn.connection.cursor()
                                    arg = (username, passw,
                                           email, name, phone, codeTMP, 0)
                                    cursor.callproc('registerUser', args=arg)
                                    conn.connection.commit()
                                    output = cursor.fetchone()
                                    output = output[0]
                            finally:
                                conn.close()

                            if output == 1:
                                
                                header = "SUPPORT"
                                body = "CÓDIGO"
                                support = "https://suport.com.do"
                                footer = "2022 © SUPPORT"

                                return await verEnvioEmail(email, codeTMP, header, body, support, footer, "CÓDIGO DE ACTIVACIÓN DE CUENTA", "Se te ha enviado un código a este correo para que actives tu cuenta.", "Usuario agregado correctamente.", "No se pudo enviar a su correo el código de activación de su cuenta.")
                            else:
                                return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "El usuario que intenta registrar ya existe.", None)
                        else:
                            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "La contraseña no cumple con los requisitos.", None)
                    else:
                        return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Número de teléfono inválido.", None)
                else:
                    return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Correo electrónico inválido.", None)
            else:
                return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Nombre de usuario inválido.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "El nombre no cumple con los requisitos.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: LOGIN *********
@user.post('/login', status_code=200, response_model=UserLogin, tags=["Usuario"])
async def login(login: UserLogin):

    # Validando que la connection sea True
    def is_empty(con):
        if con:
            return responseModelErrorX(status.HTTP_200_OK, False, "Inicio de seccion correctamente.", {"keyUser": token})
        else:
            return responseModelErrorX(status.HTTP_404_NOT_FOUND, False, "Usuario no encontrado", None)

    # CAMPO: uceCampo: username, telefono, email
    username = login.username.strip()
    username = BeautifulSoup(username, features='html.parser').text

    password = login.password.strip()
    password = BeautifulSoup(password, features='html.parser').text
    passw = password.encode()
    passw = encrytPassw(passw)

    appConnect = login.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    dataLogin = {"username": username,
                 "password": passw, "appConnect": appConnect}

    # Comprueba los campos y ejecuta las conexiones
    if verificarVacio(dataLogin) == False:

        if es_correo_valido(username) == True:

            try:
                # Usando procedimiento almacenado: loginEmail
                with engine.connect() as conn:
                    cursor = conn.connection.cursor()
                    arg = (username, passw,)
                    cursor.callproc('loginEmail', args=arg)
                    conn.connection.commit()
                    output = cursor.fetchone()
            finally:
                conn.close()

        elif es_telefono_valido(username) == True:
            username = re.sub("\!|\'|\?|\ |\(|\)|\-|\+", "", username)

            try:
                # Usando procedimiento almacenado: loginPhone
                with engine.connect() as conn:
                    cursor = conn.connection.cursor()
                    arg = (username, passw,)
                    cursor.callproc('loginPhone', args=arg)
                    conn.connection.commit()
                    output = cursor.fetchone()
            finally:
                conn.close()
        elif es_usuario_valido(username) == True:
            try:
                # Usando procedimiento almacenado: loginUser
                with engine.connect() as conn:
                    cursor = conn.connection.cursor()
                    arg = (username, passw,)
                    cursor.callproc('loginUser', args=arg)
                    conn.connection.commit()
                    output = cursor.fetchone()
            finally:
                conn.close()
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo completar la operación porque hubo un error en la validación.", None)

        if output != None:
            # Almacenamos el userID del usuario en 'userIDK'
            output = output[0]

            # Generador de token/keyUser
            token = generarToken()

            try:
                dataLogin["keyUser"] = token

                try:
                    with engine.connect() as conn:
                        conx = conn.execute(keys.insert().values(
                            keyUser=token, appConnect=appConnect, userID=output))
                finally:
                    conn.close()

                return is_empty(conx)
            except:
                return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo ejecutar la peticion.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Username y/o Password inválido/s", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: CERRAR SECCION *********
@user.post('/logout', status_code=200, response_model=UserLogout, tags=['Usuario'])
async def logout(user: UserLogout):

    appConnect = user.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    keyUser = user.keyUser.strip()
    keyUser = BeautifulSoup(keyUser, features='html.parser').text

    # Creamos un diccionario con los valores del usuario
    userArray = {"appConnect": appConnect, "keyUser": keyUser}

    # Verificamos si algun campo esta vacio
    if verificarVacio(userArray) == False:

        try:
            # Consultamos a la base de datos para obtener el userID del usuario
            with engine.connect() as conn:
                verSeccion = conn.execute(keys.select().where(
                    keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        # Verificamos si ha capturado datos.
        if verSeccion != None:

            try:
                # Consultamos a la base de datos para eliminar el usuario
                with engine.connect() as conn:
                    conn.execute(keys.delete().where(
                        keys.c.keyUser == keyUser, keys.c.appConnect == appConnect))
            finally:
                conn.close()

            return responseModelErrorX(status.HTTP_200_OK, False, "Seccion cerrada correctamente.", None)
        else:
            return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "La seccion no existe.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: OBTENER TODAS LAS APPS DEL USUARIO *********
@user.post('/getSections', status_code=200, response_model=UserSeccion, tags=['Usuario'])
async def getSections(user: UserSeccion):

    # Validando que la connection sea True
    def is_empty(con):
        if con:
            return responseModelErrorX(status.HTTP_200_OK, False, "Apps conectadas a ypwLogin", conx)
        else:
            return responseModelErrorX(status.HTTP_404_NOT_FOUND, False, "No existen apps conectadas a este usuario.", None)

    appConnect = user.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    keyUser = user.keyUser.strip()
    keyUser = BeautifulSoup(keyUser, features='html.parser').text

    # Creamos un diccionario con los valores del usuario
    userArray = {"appConnect": appConnect, "keyUser": keyUser}

    if verificarVacio(userArray) == False:

        try:
            # Peticiones a la base de datos para obtener y validar los datos ingresados por el usuario.
            with engine.connect() as conn:
                login = conn.execute(keys.select(keys.c.userID).where(
                    keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        # Verificamos con un if si el usuario ingresó correctamente sus credenciales.
        if login != None:

            try:
                # Almacenamos el userID del usuario en 'userIDU'
                userIDU = login[0]

                try:
                    with engine.connect() as conn:
                        conx = conn.execute(keys.select().where(
                            keys.c.userID == userIDU)).fetchall()
                finally:
                    conn.close()

                return is_empty(conx)
            except:
                return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo ejecutar la peticion.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "keyUser y/o appConnect inválido/s", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: CAMBIAR CONTRASEÑA DEL USUARIO *********
@user.post('/changePassword', status_code=200, response_model=ChangePassw, tags=['Usuario'])
async def changePassword(user: ChangePassw):

    appConnect = user.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    keyUser = user.keyUser.strip()
    keyUser = BeautifulSoup(keyUser, features='html.parser').text

    newPassword = user.newPassword.strip()
    newPassword = BeautifulSoup(newPassword, features='html.parser').text
    newPassw = newPassword.encode()
    newPassw = encrytPassw(newPassw)

    removeSections = user.removeSections

    # Creamos un diccionario con los valores del usuario
    userArray = {"appConnect": appConnect,
                 "keyUser": keyUser, "newPassword": newPassw}

    # Verificamos si algun campo esta vacio
    if verificarVacio(userArray) == False:

        try:
            # Consultamos a la base de datos para obtener el userID del usuario
            with engine.connect() as conn:
                vlogin = conn.execute(keys.select(keys.c.userID).where(
                    keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        # Verificamos si ha capturado datos.
        if vlogin != None:

            userIDU = vlogin[0]

            try:
                with engine.connect() as conn:
                    conn.execute(users.update().values(
                        password=newPassw).where(users.c.userID == userIDU))
            finally:
                conn.close()

            if removeSections == True:
                try:
                    with engine.connect() as conn:
                        conn.execute(keys.delete().where(
                            keys.c.userID == userIDU))
                finally:
                    conn.close()

                return responseModelErrorX(status.HTTP_200_OK, False, {
                    "m1:": "La contraseña ha sido actualizada exitosamente.",
                    "m2:": "Todas las secciones se han eliminado."
                }, None)
            else:
                return responseModelErrorX(status.HTTP_200_OK, False, "La contraseña ha sido actualizada exitosamente.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Username y/o Password inválido/s.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)

# --------- ruta: ENVIO DE CODIGO A EMAIL --------


@user.post('/setCode/email', status_code=201, response_model=SetCode, tags=['Usuario'])
async def enviarPassCodeEmail(user: SetCode):

    # >> Elimina fallas de la libreria: BeautifulSoup
    warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

    email = user.email.strip()
    email = BeautifulSoup(email, features='html.parser').text
    
    header = user.header.strip()
    header = BeautifulSoup(header, features='html.parser').text

    body = user.body.strip()
    body = BeautifulSoup(body, features='html.parser').text

    support = user.support.strip()
    support = BeautifulSoup(support, features='html.parser').text

    footer = user.footer.strip()
    footer = BeautifulSoup(footer, features='html.parser').text

    dataRecovery = {"email": email}
    arrayEmail = {"header": header, "body": body,
                  "support": support, "footer": footer}

    # Comprueba los campos y ejecuta las conexiones
    if verificarVacio(dataRecovery) == False:

        if es_correo_valido(email) == True:

            try:
                with engine.connect() as conn:
                    sql = text("select email from users where email=:email")
                    output = conn.execute(sql, email=email).first()
            finally:
                conn.close()

            if output != None:

                # Generando codigo de verificacion
                codeTMP = generarCode()

                try:
                    with engine.connect() as conn:
                        conn.execute(users.update().values(codetmp=codeTMP).where(users.c.email == email))
                finally:
                    conn.close()
                    

                if verificarVacio(arrayEmail) == False:
                    return await verEnvioEmail(email, codeTMP, header, body, support, footer, "Recuperación de contraseña", "Se te ha enviado un código como respuesta a tu peticion de recuperacion de contraseña.", "Correo enviado exitosamente.", "El correo no se pudo enviar.")
                else:
                    header = "SUPPORT"
                    body = "Su codigo de recuperacion es:"
                    support = "https://suport.com.do"
                    footer = "2022 © SUPPORT"
                        
                    return await verEnvioEmail(email, codeTMP, header, body, support, footer, "Recuperación de contraseña", "Se te ha enviado un código como respuesta a tu peticion de recuperacion de contraseña.", "Correo enviado exitosamente.", "El correo no se pudo enviar.")
            else:
                return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Correo electrónico no encontrado.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Correo electrónico inválido.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# --------- ruta: OBTENER USUARIO --------
@user.post('/changePasswCode/email', status_code=200, response_model=RecoveryPassCode, tags=['Usuario'])
async def cambiarPassCodeEmail(user: RecoveryPassCode):

    email = user.email.strip()
    email = BeautifulSoup(email, features='html.parser').text

    codetmp = user.codetmp
    code = str(codetmp).strip()
    codetmp = BeautifulSoup(code, features='html.parser').text

    newPassword = user.newPassword.strip()
    newPassword = BeautifulSoup(newPassword, features='html.parser').text

    dataRecovery = {"email": email,
                    "codetmp": codetmp, "newPassword": newPassword}

    # Comprueba los campos y ejecuta las conexiones
    if verificarVacio(dataRecovery) == False:

        if es_password_valido(newPassword) == True:
            newPassw = newPassword.encode()
            newPassw = encrytPassw(newPassw)

            if es_correo_valido(email) == True:

                if es_code_valido(codetmp) == True:
                    codetmp = int(codetmp)
                    try:
                        with engine.connect() as conn:
                            sql = text(
                                "select * from users where email=:email and codetmp=:codetmp")
                            output = conn.execute(
                                sql, email=email, codetmp=codetmp).first()
                    finally:
                        conn.close()

                    if output != None:
                        try:
                            with engine.connect() as conn:
                                conn.execute(users.update().values(password=newPassw, codetmp=None, block=0).where(
                                    users.c.codetmp == codetmp, users.c.email == email))
                                
                                #>> se eliminan todas las keys/secciones del usuario
                                userID= output["userID"]
                                conn.execute(keys.delete().where(keys.c.userID == userID))
                        finally:
                            conn.close()

                        return responseModelErrorX(status.HTTP_200_OK, False, "Contraseña ha sido restablecida exitosamente.", None)
                    else:
                        return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Código inválido.", None)
                else:
                    return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "El código introducido no cumple con los requisitos.", None)
            else:
                return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Correo electrónico inválido.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Contraseña inválida. No cumple con los requisitos.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)

"""
#********* ruta: ACTUALIZAR *********
@user.patch("/updateUser", status_code=200, response_model_exclude_unset=True, tags=["Usuario"])
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


# ********* ruta: ACTUALIZAR *********
@user.put('/updateDataUser', status_code=200, response_model=UserUpdateOpcional, response_model_exclude_unset=True, tags=["Usuario"])
async def actualizarDatos(user: UserUpdateOpcional):
        
    appConnect = user.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    keyUser = user.keyUser.strip()
    keyUser = BeautifulSoup(keyUser, features='html.parser').text

    name = user.name.strip()
    name = BeautifulSoup(name, features='html.parser').text
    
    phone = user.phone.strip()
    phone = BeautifulSoup(phone, features='html.parser').text
    
    dateOfBirth= user.dateOfBirth
    dateOfBirth = str(dateOfBirth).strip()
    dateOfBirth = BeautifulSoup(dateOfBirth, features='html.parser').text

    language = user.language
    language = str(language).strip()
    language = BeautifulSoup(language, features='html.parser').text

    country = user.country
    country = str(country).strip()
    country = BeautifulSoup(country, features='html.parser').text

    shippingAddress = user.shippingAddress
    shippingAddress= str(shippingAddress).strip()
    shippingAddress= BeautifulSoup(shippingAddress, features='html.parser').text

    identificationCard = user.identificationCard
    identificationCard = str(identificationCard).strip()
    identificationCard = BeautifulSoup(identificationCard, features='html.parser').text

    accountVersion = user.accountVersion
    accountVersion = str(accountVersion).strip()
    accountVersion = BeautifulSoup(accountVersion, features='html.parser').text

    timeZone = user.timeZone
    timeZone = str(timeZone).strip()
    timeZone = BeautifulSoup(timeZone, features='html.parser').text

    accountType = user.accountType
    accountType = str(accountType).strip()
    accountType = BeautifulSoup(accountType, features='html.parser').text

    pagWeb = user.pagWeb
    pagWeb = str(pagWeb).strip()
    pagWeb = BeautifulSoup(pagWeb, features='html.parser').text

    array = {"keyUser": keyUser, "appConnect": appConnect}

    if verificarVacio(array) == False:
        #>> Consultamos a la base de datos para obtener el userID del usuario
        try:
            with engine.connect() as conn:
                vlogin = conn.execute(keys.select(keys.c.userID).where(keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        if vlogin != None:
            #>> Tenemos el usuario: IMPORTANTE!
            userID = vlogin[0]
            
            try:
                if name:
                    if es_nombre_valido(name) == True:
                        await updateDataUser("name", name, userID)
                    else:
                        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "El dato no cumple con las condiciones.", name)
                
                if phone:
                    if es_telefono_valido(phone) == True:
                        await updateDataUser("phone", phone, userID)
                    else:
                        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "El dato no cumple con las condiciones.", phone)
                
                if dateOfBirth:
                    await updateDataUser("dateOfBirth", dateOfBirth, userID)
                    #status.append(dateOfBirth)
                
                if language:
                    await updateDataUser("language", language, userID)
                    #status.append(language)
                
                if country:
                    await updateDataUser("country", country, userID)
                    #status.append(country)
                
                if shippingAddress:
                    await updateDataUser("shippingAddress", shippingAddress, userID)
                    #status.append(shippingAddress)
                
                if identificationCard:
                    await updateDataUser("identificationCard", identificationCard, userID)
                    #status.append(identificationCard)
                
                if accountVersion:
                    await updateDataUser("accountVersion", accountVersion, userID)
                    #status.append(accountVersion)
                
                if timeZone:
                    await updateDataUser("timeZone", timeZone, userID)
                    #status.append(timeZone)
                
                if accountType:
                    await updateDataUser("accountType", accountType, userID)
                    #status.append(accountType)
                
                if pagWeb:
                    await updateDataUser("pagWeb", pagWeb, userID)
                    #status.append(pagWeb)
                
                return responseModelErrorX(status.HTTP_200_OK, False, "Datos actualizados exitosamente.", None)
            except:
                return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la petición.", None)
        else:
            return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "No se encontró la seccion.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: ACTUALIZAR *********
@user.put('/updateFieldData', status_code=200, response_model_exclude_unset=True, tags=["Usuario"])
async def actualizarCampoData(user: UpdateFieldData):

    appConnect = user.appConnect.strip()
    appConnect = BeautifulSoup(appConnect, features='html.parser').text

    keyUser = user.keyUser.strip()
    keyUser = BeautifulSoup(keyUser, features='html.parser').text

    data = user.data
    #data= str(data).strip()
    #data= BeautifulSoup(data, features='html.parser').text

    array = {"keyUser": keyUser, "appConnect": appConnect}

    if verificarVacio(array) == False:
        # Consultamos a la base de datos para obtener el userID del usuario
        try:
            with engine.connect() as conn:
                vlogin = conn.execute(keys.select(keys.c.userID).where(
                    keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
        finally:
            conn.close()

        if vlogin != None:
            userID = vlogin[0]

            if data:
                try:
                    with engine.connect() as conn:
                        conn.execute(users.update().values(
                            data=data).where(users.c.userID == userID))
                finally:
                    conn.close()

                return responseModelErrorX(status.HTTP_200_OK, False, "Datos actualizados exitosamente.", None)
            else:
                return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se enviaron datos para actualizar.", None)
        else:
            return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "No se encontró la seccion.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: INSERTAR CODIGO PARA VERIFICACION DE USUARIO *********
@user.post('/activateAccount/email', status_code=200, response_model=setCodeActivationEmail, tags=['Usuario'])
async def activateAccount(user: setCodeActivationEmail):

    email = user.email.strip()
    email = BeautifulSoup(email, features='html.parser').text

    codetmp = str(user.codetmp).strip()
    codetmp = BeautifulSoup(codetmp, features='html.parser').text

    datArray = {"email": email, "codetmp": codetmp}
    
    if verificarVacio(datArray) == False:
        if es_correo_valido(email) == True:
            
            if es_code_valido(codetmp) == True:
                
                #>> verificarCuentaRegistrada: email
                data= verCuentaRegistrada(email)
                
                if data != None:
                    #>> verificarCuentaActivada: email, code
                    dataUser= verCuentaActivada(email, codetmp)

                    if dataUser != None:
                        passw= dataUser["password"]
                        #>> generar token= keyUser
                        token= generarToken()

                        try:
                            with engine.connect() as conn:
                                conn.execute(users.update().values(codetmp=None, block=0).where(users.c.email == email))
                            
                                #>> autoLogin: email, password
                                login= autoLogin(email, passw)
                                
                                conn.execute(keys.insert().values(keyUser=token, appConnect="default", userID=login))
                                conn.connection.commit()
                        finally:
                            conn.close()

                        return responseModelErrorX(status.HTTP_200_OK, False, "Usuario verificado exitosamente.", {"appConnect": "default", "keyUser": token})
                    else:
                        return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Código inválido, o esta cuenta ya ha sido verificada anteriormente.", None)
                else:
                    return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
            else:
                return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "El código introducido no cumple con los requisitos.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Correo electrónico inválido.", None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)


# ********* ruta: INSERTAR CODIGO PARA VERIFICACION DE USUARIO *********
@user.post('/uploadImageProfile', status_code=200, response_model=uploadImageProfile, tags=['Usuario'])
async def subirImagenPerfil(img: uploadImageProfile):
    
    try:
        username= img.username.strip()
        username= BeautifulSoup(username, features='html.parser').text
        
        imagenBytes= img.imagenPerfil
        
        #>> inserta la imagen del producto en la carpeta data/profile
        await bytesToImage(imagenBytes, username)
        
        return responseModelErrorX(status.HTTP_200_OK, False, "Imagen de Perfil guardada exitosamente.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo subir la imagen.", None)



# ********* ruta: OBTENER TODAS LAS APPS DEL USUARIO *********
@user.post('/deleteAccount', status_code=200, response_model=DeleteAccount, tags=['Usuario'])
async def eliminarCuenta(user: DeleteAccount):
    
    email= user.email.strip()
    email= BeautifulSoup(email, features='html.parser').text
    
    password= user.password.strip()
    password= BeautifulSoup(password, features='html.parser').text
    passw = password.encode()
    passw = encrytPassw(passw)
    
    userArray= {"email": email, "password": passw}
    
    try:
        if verificarVacio(userArray) == False:
            if es_correo_valido(email) == True:
                
                data= await qIntraLogin(email, passw)
                
                if data != None:
                    userID= data["userID"]
                    
                    await qEliminarCuenta(email, userID)
                    
                    header = "Usted ha eliminado su cuenta"
                    body = "Su cuenta ha sido eliminada de manera exitosa."
                    support = "https://suport.com.do"
                    footer = "2022 © SUPPORT"
                        
                    return await verEnvioEmail(email, email, header, body, support, footer, "Usted ha eliminado su cuenta", "Su cuenta ha sido eliminada de manera exitosa.", "Cuenta eliminada exitosamente.", "El correo no se pudo enviar.")
                else:
                    return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
            else:
                return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Correo electrónico inválido.", None)
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la peticion.", None)


#>> metodo para autenticar el usuario developer
"""
@user.get('/developer/me', status_code=200, tags=['Usuario'])
async def readME(permiso: str = Depends(get_current_username)):
    
    return responseModelErrorX(status.HTTP_200_OK, False, "Usuario confirmado.", None)
"""