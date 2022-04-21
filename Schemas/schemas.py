from datetime import datetime
from time import *
from pydantic import BaseModel, Field
from typing import *
from typing import TypedDict
from bs4 import BeautifulSoup

def stripTarget(cadena):
    tex = BeautifulSoup(cadena, features='html.parser').text
    return tex


#***** MODELO CLIENTE: solicitud *****
class UserRequestModel(BaseModel):
    username: Optional[str]= ""
    password: Optional[str]= ""
    name: Optional[str]= ""
    email: Optional[str]= ""
    phone: Optional[str]= ""
    dateOfBirth: Optional[str]= ""
    language: Optional[str]= ""
    country: Optional[str]= ""
    ypwCashBalance: Optional[str]= ""
    shippingAddress: dict #JSON
    identificationCard: Optional[str]= ""
    accountVersion: Optional[str]= ""
    timeZone: Optional[str]= ""
    recoveryCode: Optional[str]= ""
    applications: dict #JSON
    limitations: dict  #JSON
    accountType: Optional[str]= ""
    tradingExits: dict #JSON
    pendingInvoices: dict  #JSON
    bills: dict  #JSON
    subscriptions: dict  #JSON
    metodoPago: Optional[str]= ""
    servidorDB: Optional[str]= ""
    userDB: Optional[str]= ""
    puertoDB: Optional[str]= ""
    pagWeb: Optional[str]= ""

    class Config:
        arbitrary_types_allowed = True


class UserResponseModel(UserRequestModel):
    userID: int


#***** REGISTRO ***** modelo
class UserRegistro(BaseModel):
    username: str
    password: str
    name: str
    email: str


#***** LOGIN ****** modelo
class UserLogin(BaseModel):
    appConnect: str
    username: str
    password: str


#**** OBTENER USUARIO **** modelo
class UserObtener(BaseModel):
    appConnect: str
    key: str


#**** MODELOS DE ERRORES HTTPEXCEPTION **** modelo
