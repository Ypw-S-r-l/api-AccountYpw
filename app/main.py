from fastapi import FastAPI, Request
import uvicorn
from Routes.user import user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from Database.conexion import conn
from config.methods import APIversion


description = """
AccountYPW API helps you do awesome stuff. 🚀

## Users

You will be able to:

* **Register users** (_implemented_).
* **Login users** (_implemented_).
* **Logout users** (_implemented_).
* **Get users** (_implemented_).
* **Get sections** (_implemented_).
* **Change password** (_implemented_).
* **Set recovery code** (_implemented_).
* **Change password code** (_implemented_).
* **Update all data user** (_implemented_).
"""

version= APIversion()

app = FastAPI(debug=True,
    title="Account YPW",
    description=description,
    version= version[1],
    terms_of_service="https://ypw.com.do/",
    contact={
        "name": "YPW.SRL - Yolfri Páginas Web",
        "url": "https://ypw.com.do/",
    })


#-------- Eventos para validar conexion a DB
@user.on_event("startup")
async def startup():
    if conn.close:
        conn.connect()
    print("Application startup")

@user.on_event("shutdown")
async def shutdown():
    if not conn.close:
        conn.close()
    print("Application shutdown")

#Funcion para responder cuando el usuario ingrese una ruta invalida
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({
            "error": True,
            "message": "Ruta invalida.",
            "res": None,
            "version": version[1]
        })
    )

#Funcion para responder cuando faltan campos
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "error": True,
            "message": "Inexistencia de campos.",
            "res": None,
            "version": version[1]
        })
    )

#Solucion CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__=='__main__':
    uvicorn.run(app, host="0.0.0.0", port="8000")

#>> conexion a user de Routes
app.include_router(user)