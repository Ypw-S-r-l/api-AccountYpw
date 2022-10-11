from starlette.status import *
from fastapi import status
from bs4 import BeautifulSoup
from sqlalchemy import text
from Models.index import users, keys, dataTable
from Schemas.schemas import *
from config.methods import *
from config.regexp import *
from Routes.user import user #APIRouter



@user.post('/data/get', tags=["Data"])
async def dataGet(dat: DataGetKeyData):
    
    appConnect= dat.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= dat.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    keyData= dat.keyData.strip()
    keyData= BeautifulSoup(keyData, features='html.parser').text
    
    try:
        if appConnect and keyUser and keyData:
            #>> globalUser del usuario
            data= await qVerificarKeyUser(appConnect, keyUser)
            
            if data!=None:
                userID= data[0]
                #>> keydata del usuario
                keydatos= await qObtenerKeyData(userID, keyData)
                
                if keydatos:
                    return responseModelErrorX(status.HTTP_200_OK, False, f"KeyData: {keyData}", keydatos)
                else:
                    return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "KeyData no existente.", None)
            else:
                return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la peticion.", None)


#>> metodo get data
@user.post('/data/getAll', tags=["Data"])
async def dataGetAll(dat: DattGeneral):
    
    appConnect= dat.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text

    keyUser= dat.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    try:
        if appConnect and keyUser:
            #>> globalUser del usuario
            data= await qVerificarKeyUser(appConnect, keyUser)
            
            if data!=None:
                userID= data[0]
                #>> keydata del usuario
                keydatos= await qObtenerAllKeyData(userID)
                
                if keydatos:
                    return responseModelErrorX(status.HTTP_200_OK, False, "KeyData existentes.", keydatos)
                else:
                    return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "No existen keyData.", None)
            else:
                return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la peticion.", None)


#>> metodo set data
@user.post('/data/create', tags=["Data"])
async def dataCreate(dat: DataCreateSetData):
    
    appConnect= dat.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text
    
    keyUser= dat.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    keyData= dat.keyData.strip()
    keyData= BeautifulSoup(keyData, features='html.parser').text
    
    data= dat.Data
    
    try:
        if appConnect and keyUser and keyData:
            #>> globalUser del usuario
            dataUser= await qVerificarKeyUser(appConnect, keyUser)
            
            if dataUser!=None:
                userID= dataUser[0]
                #>> keydata del usuario
                ex= await qInsertarDataKeyData(userID, keyData, data)
                
                if ex==None:
                    return responseModelErrorX(status.HTTP_201_CREATED, False, "Datos insertados correctamente.", None)
                else:
                    return responseModelErrorX(status.HTTP_200_OK, True, "Datos no insertados.", None)
            else:
                return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la peticion.", None)


#>> metodo set data
@user.put('/data/set', tags=["Data"])
async def dataSet(dat: DataCreateSetData):
    
    appConnect= dat.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text
    
    keyUser= dat.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    keyData= dat.keyData.strip()
    keyData= BeautifulSoup(keyData, features='html.parser').text
    
    data= dat.Data
    
    try:
        if appConnect and keyUser and keyData:
            #>> globalUser del usuario
            dataUser= await qVerificarKeyUser(appConnect, keyUser)
            
            if dataUser!=None:
                userID= dataUser[0]
                #>> keydata del usuario
                keydatav2= await qVerificarKeyData(userID, keyData)
                
                if keydatav2!=None:
                    try:
                        await qUpdateFieldData(userID, keyData, data)
                        
                        return responseModelErrorX(status.HTTP_200_OK, False, "Data actualizada.", None)
                    except:
                        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Data no pudo ser actualizada.", None)
                else:
                    return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "KeyData no encontrada.", None)
            else:
                return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la peticion.", None)


#>> metodo set data
@user.delete('/data/remove', tags=["Data"])
async def dataRemove(dat: DataRemoveData):
    
    appConnect= dat.appConnect.strip()
    appConnect= BeautifulSoup(appConnect, features='html.parser').text
    
    keyUser= dat.keyUser.strip()
    keyUser= BeautifulSoup(keyUser, features='html.parser').text
    
    keyData= dat.keyData.strip()
    keyData= BeautifulSoup(keyData, features='html.parser').text
    
    try:
        if appConnect and keyUser and keyData:
            #>> globalUser del usuario
            dataUser= await qVerificarKeyUser(appConnect, keyUser)
            
            if dataUser!=None:
                userID= dataUser[0]
                #>> keydata del usuario
                keydatav2= await qVerificarKeyData(userID, keyData)
                
                if keydatav2!=None:
                    try:
                        await qDeleteKeyData(userID, keyData)
                        
                        return responseModelErrorX(status.HTTP_200_OK, False, "keyData eliminada correctamente.", None)
                    except:
                        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "keyData no pudo ser eliminada.", None)
                else:
                    return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "KeyData no encontrada.", None)
            else:
                return responseModelErrorX(status.HTTP_404_NOT_FOUND, True, "Usuario no encontrado.", None)
        else:
            return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "Existen campos vacios.", None)
    except:
        return responseModelErrorX(status.HTTP_400_BAD_REQUEST, True, "No se pudo realizar la peticion.", None)