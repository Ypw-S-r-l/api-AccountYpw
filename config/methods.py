from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#Metodos de control de versiones
def APIversion():
    verApi= ("v1", "v1.3.5")
    return verApi

version= APIversion()

#Metodo para enviar respuesta 200 ~
def responseModelError2X(status_code, error: bool, message, res):
    return JSONResponse(
        status_code= status_code,
        content=jsonable_encoder({
            "error": error,
            "message": message,
            "res": res,
            "version": version[1]
        }),
    )

#Metodo para enviar respuesta 400 ~
def responseModelError4X(status_code, error: bool, message, res):
    return JSONResponse(
        status_code= status_code,
        content=jsonable_encoder({
            "error": error,
            "message": message,
            "res": res,
            "version": version[1]
        }),
    )
