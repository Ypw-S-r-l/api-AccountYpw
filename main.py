from fastapi import FastAPI
from Database.conexion import engine as connection
from Routes.user import user
from fastapi.middleware.cors import CORSMiddleware
#from Schemas.schemas import UserRequestModel


app = FastAPI(title="ApiLogin YPW",
    description="ApiLogin general YPW",
    version="v0.1")


#Solucion CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#>> conexion a user de Routes
app.include_router(user)