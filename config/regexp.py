import re


#>> VALIDANDO EMAIL: expresiones regulares
def es_correo_valido(correo):
    expresion_regular = r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$"
    return re.match(expresion_regular, correo) is not None


#>> VALIDANDO PHONE: expresiones regulares
def es_telefono_valido(phone):
    expresion_regular = r"^[+]?(\d{1,4})?\s?-?[.]?[(]?\d{3}[)]?\s?-?[.]?\d{3}\s?-?[.]?\d{4}$"
    return re.match(expresion_regular, phone) is not None


#>> VALIDANDO USERNAME: expresiones regulares
def es_usuario_valido(username):
    expresion_regular = r"^[a-zA-Z0-9@]+[._a-zA-Z0-9@]{3,34}$"
    return re.match(expresion_regular, username) is not None


#>> VALIDANDO PASSWORD: expresiones regulares
def es_password_valido(password):
    expresion_regular = r"^\S(.|\s){7,200}$"
    return re.match(expresion_regular, password) is not None


#>> VALIDANDO NAME: expresiones regulares
def es_nombre_valido(name):
    expresion_regular = r"^([a-zA-Záéíóúñ. ]{1,40}\s?){1,5}$"
    return re.match(expresion_regular, name) is not None


#>> VALIDANDO CODE: expresiones regulares
def es_code_valido(code):
    expresion_regular = r"^\d{6}$"
    return re.match(expresion_regular, code) is not None
