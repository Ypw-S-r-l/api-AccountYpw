from fastapi import FastAPI, Request
import uvicorn, asyncio
from Database.conexion import engine as connection
from Routes.user import user
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
#from Schemas.schemas import UserRequestModel

description = """
LoginYPW API helps you do awesome stuff. 🚀

## Users

You will be able to:

* **Register users** (_implemented_).
* **Login users** (_implemented_).
* **Get users** (_implemented_).
"""

app = FastAPI(debug=True,
    title="ApiLogin YPW",
    description=description,
    version="v1",
    terms_of_service="https://ypw.com.do/",
    contact={
        "name": "YPW.SRL - Yolfri Páginas Web",
        "url": "https://ypw.com.do/",
    })


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse({
        "error": True,
        "message": "Ruta invalida.",
        "res": None,
        }
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