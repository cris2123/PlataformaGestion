import os

## Path para los archivos
PROJECT_ROOT= os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INTERMEDIATE_PATH=os.path.join(PROJECT_ROOT,'BIOLAC')
STATIC_FOLDER=os.path.join(INTERMEDIATE_PATH,'static')
UPLOAD_FOLDER= os.path.join(STATIC_FOLDER,'uploads')

## Extensiones para archivos de perfil
ALLOWED_AVATAR_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
## Extensiones para carga de documentos a evaluar
ALLOWED_DOCUMENT_EXTENSIONS = set(['pdf', 'gif', 'jpeg', 'png'])

## Constantes para usar flask_principal para el sistema de roles
ROLES={"1":"admin","2":"estandar","3":"asistentes","4":"evaluadores"}

## Datos para el envio del correo en jinja
IP="192.168.1.106:5000"
SUBJECT= "Confirmacion del correo para ingresar a la plataforma UNU-BIOLAC"
SUBJECT_RESEND= "Reenvio del correo para ingreso al sistema de UNU-BIOLAC"
SUBJECT_PASSWORD=" Recuperación de la contraseña de la plataforma UNU-BIOLAC"
SUBJECT_INVITATION=" Solicitud para ser evaluador en la plataforma de Biolac"
DUMMY_MAIL=""

## Variable para deployment
# IP="domain name with ruta "
#DUMMY_MAIL="correo para las pruebas aws"
IP_DOMAIN="http://localhost:5000"

