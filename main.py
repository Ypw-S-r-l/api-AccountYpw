from fastapi import FastAPI
import uvicorn
from Database.conexion import engine as connection
from Routes.user import user
from fastapi.middleware.cors import CORSMiddleware
#from Schemas.schemas import UserRequestModel


app = FastAPI(debug=True,
    title="ApiLogin YPW",
    description="ApiLogin general YPW",
    version="v1")


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
    uvicorn.run(app, host="127.0.0.1", port="8000")

#>> conexion a user de Routes
app.include_router(user)