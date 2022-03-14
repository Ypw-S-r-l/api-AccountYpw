from dataclasses import dataclass
import json
from time import *
from unicodedata import name
from pydantic import BaseModel, Field
from typing import *
from typing import Dict
from datetime import datetime
from sqlalchemy import JSON


"""
class shippingAddress(BaseModel):
    name: str
    surname: str
    company: str 
    direction: str 
    apartment: str 
    city: str
    state: str 
    zipCode: str 
    region: str

    class Config:
        orm_mode: True
#shippingAddress = json.loads(shippingAddress)
"""

"""
class subscription(BaseModel):
    name: str
    cuota: str
    precio: str

    class Config:
        orm_mode: True
#subscription = json.loads(subscription)
"""

"""
class limitations(BaseModel):
    locks: str
    message: str
    canNotAccess: str
    limitRemovalDate: str

    class Config:
        orm_mode: True
#limitations = json.loads(limitations)
"""

suscripcion = {
    "cuota": ""
}


#subscription: List[str] = []
#***** MODELO CLIENTE: solicitud *****
class UserRequestModel(BaseModel):
    username: Optional[str]
    password: Optional[str]
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    dateOfBirth: Optional[str]
    language: Optional[str]
    country: Optional[str]
    ypwCashBalance: Optional[str]
    shippingAddress: Optional[str] #List
    identificationCard: Optional[str]
    accountVersion: Optional[str]
    timeZone: Optional[str]
    recoveryCode: Optional[str]
    applications: Optional[str] #List
    limitations: Optional[str] #List
    accountType: Optional[str]
    tradingExits: Optional[str] #List
    pendingInvoices: Optional[str] #List
    bills: Optional[str] #List
    subscriptions: Optional[str] #List
    metodoPago: Optional[str]
    servidorDB: Optional[str]
    userDB: Optional[str]
    puertoDB: Optional[str]
    pagWeb: Optional[str]

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
    username: str
    keyUser: str











#***** ACTUALIZAR: datos personales ****** modelo
class dataPersonalUpdate(BaseModel):
    username: str
    password: str
    name: str
    email: str
    phone: str
    dateOfBirth: str
    language: str
    country: str

#***** ACTUALIZAR: datos generales ****** modelo
class dataGeneralUpdate(BaseModel):
    ypwCashBalance: str
    shippingAddress: str
