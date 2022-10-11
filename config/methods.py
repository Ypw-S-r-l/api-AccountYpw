import base64
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status
from config.email import enviarEmail
from sqlalchemy import text
from Models.index import users, keys, apiKey, dataTable
from Database.conexion import engine

# Metodos de control de versiones
def APIversion():
    verApi = ("v1", "v1.4.10")
    return verApi

version = APIversion()


# Metodo para enviar respuesta 200 ~
def responseModelErrorX(status_code, error: bool, message, res):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "error": error,
            "message": message,
            "res": res,
            "version": version[1]
        }),
    )


#>> Consulta para confirmar el si el usuario tiene su cuenta ya activada
def verCuentaActivada(email: str, code):
    try:
        with engine.connect() as conn:
            data= conn.execute(users.select().where(users.c.email == email, users.c.codetmp == code)).first()
        
        return data
    finally:
        conn.close()


#>> Consulta para confirmar el si el usuario esta registrado
def verCuentaRegistrada(email: str):
    try:
        with engine.connect() as conn:
            data = conn.execute(users.select().where(users.c.email == email)).first()

        return data
    finally:
        conn.close()


#>> FUNCION PARA AUTOLOGIN AL REGISTRARSE
def autoLogin(email, passw):
    arg = (email, passw,)

    try:
        with engine.connect() as conn:
            cursor = conn.connection.cursor()
            cursor.callproc('loginEmail', args=arg)
            conn.connection.commit()
            output = cursor.fetchone()
            userID = output[0]
    finally:
        conn.close()
    return userID


#>> Verificar el envio del cbodyorreo: capturando errores
async def verEnvioEmail(email, codeTMP, header, body, support, footer, titulo, asunto, resPositiva: str, resNegativa: str):
    if enviarEmail(email, codeTMP, header, body, support, footer, titulo, asunto) == None:
        return responseModelErrorX(status.HTTP_200_OK, False, resPositiva, None)
    else:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, resNegativa, None)



#>> consulta para insertar imagen de los articulos/productos
async def bytesToImage(imagen: bytes, username: str):
    try:
        #>> decodeamos la imagen (de bytes a img)
        img= base64.decodebytes(imagen)
        #>> colocamos nombre a la foto
        filename= f"{username}.jpg"
        
        #>> creamos la imagen
        with open('./data/profile/'+filename, 'wb') as file:
            file.write(img)
    finally:
        file.close()


#>> consulta para actualizar datos del usuario
async def updateDataUser(campo, dato, userID):
    try:
        with engine.connect() as conn:
            sql= text(f"update users set {campo}=:dato where userID=:userID")
            conn.execute(sql, dato=dato, userID=userID)
            conn.connection.commit()
    finally:
        conn.close()


#>> login interno
async def qIntraLogin(email, passw):
    try:
        with engine.connect() as conn:
            data= conn.execute(users.select().where(users.c.email == email, users.c.password == passw)).first()
        return data
    finally:
        conn.close()


#>> eliminar cuenta de usuario
async def qEliminarCuenta(email, userID):
    try:
        with engine.connect() as conn:
            conn.execute(users.delete().where(users.c.email == email))
            conn.execute(keys.delete().where(keys.c.userID == userID))
    finally:
        conn.close()

#>> eliminar todas las secciones de un usuario
async def qEliminarSesiones(userID):
    try:
        with engine.connect() as conn:
            conn.execute(keys.delete().where(keys.c.userID == userID))
    finally:
        conn.close()

#>> insertar keyData en data
async def qInsertarDataKeyData(userID, keyData, data):
    try:
        with engine.connect() as conn:
            conn.execute(dataTable.insert().values(userID=userID, keyData=keyData, Data=data))
    finally:
        conn.close()

#>> consultamos a la base de datos para obtener el userID del usuario
async def qVerificarKeyUser(appConnect, keyUser):
    try:
        with engine.connect() as conn:
            vdata= conn.execute(keys.select(keys.c.userID).where(
                keys.c.keyUser == keyUser, keys.c.appConnect == appConnect)).first()
            return vdata
    finally:
        conn.close()

#>> obtener keyData en tabla data
async def qObtenerKeyData(userID):
    try:
        with engine.connect() as conn:
            datos= conn.execute(dataTable.select().where(dataTable.c.userID == userID)).fetchall()
            return datos
    finally:
        conn.close()

async def qVerificarKeyData(userID, keyData):
    try:
        with engine.connect() as conn:
            datos= conn.execute(dataTable.select().where(dataTable.c.keyData == keyData, dataTable.c.userID == userID)).first()
            return datos
    finally:
        conn.close()

async def qUpdateFieldData(userID, keyData, data):
    try:
        with engine.connect() as conn:
            conn.execute(dataTable.update().values(Data=data).where(dataTable.c.keyData == keyData, dataTable.c.userID == userID))
    finally:
        conn.close()

async def qDeleteKeyData(userID, keyData):
    try:
        with engine.connect() as conn:
            conn.execute(dataTable.delete().where(dataTable.c.keyData == keyData, dataTable.c.userID == userID))
    finally:
        conn.close()