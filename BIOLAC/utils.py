import string
import random
import os
from datetime import datetime
from time import gmtime, strftime
from constants import ALLOWED_AVATAR_EXTENSIONS,ALLOWED_DOCUMENT_EXTENSIONS
from werkzeug.utils import secure_filename


def make_dir_user_folder(root,folder):

    full_path=os.path.join(root,folder)

    if not os.path.exists(full_path):
        try:
            os.mkdir(full_path)
            print("Carpeta creada")
            return(full_path)

        except Exception as e:

            raise e


def parsing_data(data):

    role=data.split(',',1)[0]
    role=role.replace("(","")
    role=role.replace(")","")
    role=role.replace("'","")
    return(role)

# def saving_files(fellow_document):
#
#     """ Funcion para cargar los arhibos subidos en el filesystem
#     request: Esta variable es el objeto obtenido de request.form['file']"""
#
#     path=""
#     if fellow_document.filename =='':
#         file_path="No hay ningun archivo"
#         return(file_path)
#
#     else:
#         if fellow_document and _allowed_file(fellow_document.filename,ALLOWED_DOCUMENT_EXTENSIONS):
#             filename = secure_filename(fellow_document.filename)
#
#             if not os.path.exists(app.config['UPLOAD_FOLDER']):
#                 make_dir(app.config['UPLOAD_FOLDER'])
#
#             path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             try:
#                 fellow_document.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 return(path)
#             except Exception as e:
#                 return("Ocurrio un error" + str(e))


def next_is_valid(uri,role):

    """ Debo pensar mejor esta funcion, pero tiene 2 objetivos muy importantes
    la primera es evitar que  un usuario que haya descubierto al link de fun
    ciones de administrador trate de llegar a ese endpoint le den la opcion de
    loguearse por el decorador login required y al loguearse tenga acceso a la
    funcion dado que en ese momento no se valida su rol.
    La segunda es evitar que de alguna manera esten tratando de hacer open
    redirects asi que tengo que validar todos los endpoint de mi aplicacion
    para evitar robo de credenciales para los usuarios """

    ## Falta hacer una lista de urls
    # if endpoint==None:
    #     return(True)
    endpoints=["/delete","/restore","/backup"]

    if uri in endpoints and role != "admin":
        return(False)

    else:
        return(True)

def get_time():
    """ Obtengo la hora actual del servidor """
    return( datetime.now().time() )

def currentStrDate():
    """ Devuelve un string con la fecha actual """
    return(strftime("%Y-%m-%d", gmtime()))

def currentDate():
    """ Devuelve la fecha actual en formato datetime (util para la db)"""
    return(datetime.now())

def generate_key():
    """ Codigo para generar la llave secreta de la aplicacion.
    Se utilizara la libreria os para usar urandom y crear una llave aleatoria"""

    try:
        key=os.urandom(24)
        assert (isinstance(key,bytes)),"urandom didnt give correct type!!"
    except Exception:
        print("Get and error with key generator")
        sys.exit(0)
    return(key)

def pattern_verifier(password):

    """ Verifico que el password en python este construido de la forma correcta
    -Al menos una mayuscula
    -Al menos una minuscula
    -Al menos un numero
    -Al menos un caracter de la lista -,_,$,&,%,*,!,<,>,',",?,@,#,^,=,+

     """
    #assert (isinstance(password,str)), "El password debe ser un string"
    try:
        pattern=re.compile(\
        '(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-,_,$,&,%,*,!,<,>,",?,@,#,^,=,+]).{6,20}')
        result=pattern.match(password)

    except(AttributeError,TypeError):

        raise AssertionError('Input variables should be strings')

    except(re.error):

        print("Error con el error del patron del regex o el regex en match()")

    else:
        if result:
        	return(True)
        else:
        	return(None)

def _hashing_password(password,bcrypt):
    """ Funcion que me permite generar un hash con el algoritmo bcrypt
    Implementado en python """

    ## Existen 2 maneras de evitar las referencias circulares en el caso
    ## de este modulo, la primera es importar bcrypt del modulo principal
    ## dentro de la funcion.

    ## La segunda forma es pasar a la funcion el parametro bcrypt seteado
    ## en el otro modulo. Me parece mas pythonic la segunda pero la primera
    ## es valida

    #from main import bcrypt

    try:
        user_hash=bcrypt.generate_password_hash(password)
    except(AttributeError,TypeError):
        raise AssertionError("El password debe ser un string")
    except Exception:
        print("Ocurrio un error no conocido")
    else:
        if user_hash:
            return(user_hash)
        else:
            print("Hubo un error extra no controlado")
            sys.exit(0)

def make_dir(dir_path):

    """ Funcion para crear directorios en el filesystem eso lo usare para
    crear directorios separados para cada usuario y sus archivos """

    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception as e:
        raise e

def _allowed_file(filename,restricted_files):

    return("." in filename and filename.rsplit('.',1)[1] in\
    restricted_files)


def _key2num(query):

    """Esta funcion es para parsear las llaves y la base de datos, tengo
    que mejorarla mucho para obteenr los datos que necesito """
    char='(),'
    result=''
    for c in query:
        if c not in char:
            result=result + c
        else:
            pass
    key=int(result)
    return(key)

def detecting_dynamic(request):
    """Funcion utilizada para detectar cuantas llaves existen en un request y
    popular el objeto

    number_mapping= Es un arreglo que guardara la cantidad de objetos generados
    en los campos dinamicos de las formas

     """

    number_mapping=[]
    cObjectives=0
    cCollaborators=0
    cBudgetItems=0

    for key in request:
        if "courseObjectives" in key:
            cObjectives+=1
    number_mapping.append(cObjectives)
    return(number_mapping)




if __name__=="__main__":

    pass
