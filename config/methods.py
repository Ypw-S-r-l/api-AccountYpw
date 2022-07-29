from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

#Metodo de control de versiones 
def APIversion():
    verApi= "v1.3.0"
    return verApi


#Metodo para enviar respuesta 200 ~
def responseModelError2X(status_code, error: bool, message, res):
    return JSONResponse(
        status_code= status_code,
        content=jsonable_encoder({
            "error": error,
            "message": message,
            "res": res,
            "version": APIversion()
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
            "version": APIversion()
        }),
    )