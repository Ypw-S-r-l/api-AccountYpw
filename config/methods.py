from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status
from config.email import enviarEmail
from sqlalchemy import text
from Models.index import users, keys
from Database.conexion import engine

# Metodos de control de versiones
def APIversion():
    verApi = ("v1", "v1.4.0")
    return verApi

version = APIversion()

# Metodo para enviar respuesta 200 ~
def responseModelError2X(status_code, error: bool, message, res):
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "error": error,
            "message": message,
            "res": res,
            "version": version[1]
        }),
    )

# Metodo para enviar respuesta 400 ~
def responseModelError4X(status_code, error: bool, message, res):
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
def verEnvioEmail(email, codeTMP, header, body, support, footer, titulo, asunto, resPositiva: str, resNegativa: str):
    if enviarEmail(email, codeTMP, header, body, support, footer, titulo, asunto) == None:
        return responseModelError2X(status.HTTP_200_OK, False, resPositiva, None)
    else:
        return responseModelError4X(status.HTTP_400_BAD_REQUEST, True, resNegativa, None)