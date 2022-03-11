from fastapi import FastAPI
from Database.conexion import engine as connection
from Routes.user import user
#from Schemas.schemas import UserRequestModel

app = FastAPI(title="ApiLogin YPW",
    description="ApiLogin general YPW",
    version="v0.1")

#>> conexion a user de Routes
app.include_router(user)