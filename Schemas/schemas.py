from time import *
from pydantic import BaseModel, EmailStr, Field
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
    username: Optional[str]= ""
    name: Optional[str]= ""
    phone: Optional[str]= ""
    
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
    dateOfBirth: Optional[str]= ""
    language: Optional[str]= ""
    country: Optional[str]= ""
    ypwCashBalance: Optional[str]= ""
    shippingAddress: Optional[dict] #JSON
    identificationCard: Optional[str]= ""
    accountVersion: Optional[str]= ""
    timeZone: Optional[str]= ""
    recoveryCode: Optional[str]= ""
    applications: Optional[dict] #JSON
    limitations: Optional[dict]  #JSON
    accountType: Optional[str]= ""
    tradingExits: Optional[dict] #JSON
    pendingInvoices: Optional[dict]  #JSON
    bills: Optional[dict]  #JSON
    subscriptions: Optional[dict]  #JSON
    metodoPago: Optional[str]= ""
    servidorDB: Optional[str]= ""
    userDB: Optional[str]= ""
    puertoDB: Optional[str]= ""
    pagWeb: Optional[str]= ""
    data: Optional[dict]  #JSON

    class Config:
        arbitrary_types_allowed = True