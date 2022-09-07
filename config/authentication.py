import base64
from fastapi import Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from bs4 import BeautifulSoup
from Database.conexion import engine
from config.methods import responseModelErrorX
from Models.index import apiKey


#>> Esquema HTTPBasic Authentication
security= HTTPBasic()


#>> AUTORIZACION PARA UTILIZAR LA API
def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    
    try:
        usernameBytes= BeautifulSoup(credentials.username.strip(), features='html.parser').text
        username = base64.b64decode(usernameBytes).decode("utf-8")
        
        passwordBytes= BeautifulSoup(credentials.password.strip(), features='html.parser').text
        password = base64.b64decode(passwordBytes).decode("utf-8")
    
        with engine.connect() as conn:
            data= conn.execute(apiKey.select().where(apiKey.c.CLIENT_KEY == username, apiKey.c.CLIENT_SECRET == password)).first()
        
        if data != None:
            return responseModelErrorX(status.HTTP_200_OK, None, "Peticion exitosa.", None)
        else:
            return responseModelErrorX(status.HTTP_401_UNAUTHORIZED, True, "Email o Password incorrecto.", None)
    finally:
        conn.close()

