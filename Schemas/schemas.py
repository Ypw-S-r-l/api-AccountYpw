from time import *
from pydantic import BaseModel, Field
from typing import *
from typing import TypedDict
from bs4 import BeautifulSoup

def stripTarget(cadena):
    tex = BeautifulSoup(cadena, features='html.parser').text
    return tex


#***** MODELO CLIENTE: actualizar datos principales *****
class UserUpdate(BaseModel):
    appConnect: str
    keyUser: str
    username: Optional[str]= Field(None)
    name: Optional[str]= Field(None)
    phone: Optional[str]= Field(None)
    
    class Config:
        arbitrary_types_allowed= True


#***** REGISTRO ***** modelo
class UserRegistro(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str


#***** LOGIN ****** modelo
class UserLogin(BaseModel):
    username: str
    password: str
    appConnect: str


#**** OBTENER USUARIO **** modelo
class UserObtener(BaseModel):
    appConnect: str
    keyUser: str


#***** LOGOUT: cerrar seccion ****** modelo
class UserLogout(BaseModel):
    appConnect: str
    keyUser: str


#***** OBTENER SECCIONES ****** modelo
class UserSeccion(BaseModel):
    appConnect: str
    keyUser: str

#***** CAMBIAR PASSWORD ****** modelo
class ChangePassw(BaseModel):
    appConnect: str
    keyUser: str
    newPassword: str
    removeSections: bool= False

#***** ENVIAR CODIGO POR CORREO ****** modelo
class SetCode(BaseModel):
    email: str
    header: Optional[str]= ""
    body: Optional[str]= ""
    support: Optional[str]= ""
    footer: Optional[str]= ""

#***** RECUPERAR PASSWORD POR CODIGO ****** modelo
class RecoveryPassCode(BaseModel):
    email: str
    codetmp: str
    newPassword: str


#***** MODELO CLIENTE: actualizar datos secundarios *****
class UserUpdateOpcional(BaseModel):
    appConnect: str
    keyUser: str
    name: Optional[str]= ""
    dateOfBirth: Optional[str]= ""
    language: Optional[str]= ""
    country: Optional[str]= ""
    shippingAddress: Optional[dict] #JSON
    identificationCard: Optional[str]= ""
    accountVersion: Optional[str]= ""
    timeZone: Optional[str]= ""
    accountType: Optional[str]= ""
    pagWeb: Optional[str]= ""
    data: Optional[dict]  #JSON

    class Config:
        arbitrary_types_allowed = True


class UpdateFieldData(BaseModel):
    appConnect: str
    keyUser: str
    data: dict #JSON