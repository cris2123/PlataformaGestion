import os
import datetime
import re
import pdfkit
from flask import Flask , render_template, send_from_directory, request,\
    current_app, flash, abort, redirect , url_for ,jsonify , make_response
from flask_principal import Principal, Permission,RoleNeed, Identity, AnonymousIdentity,\
    identity_changed, UserNeed, identity_loaded
from flask import session as s
from werkzeug.utils import secure_filename


from utils import generate_key, next_is_valid, _allowed_file , make_dir, detecting_dynamic,\
    parsing_data,make_dir_user_folder

from database import dbSession, session_manager ,Base , engine ,init_db, drop_db
from models import User , Role, Permisos ,DocumentosCursos,\
    CourseObjectives, Fellow ,FellowDocuments, Curso , CourseBudgetsItems,\
    CourseCollaborators, FellowObjectives, FellowActivities,EvaluationFellows,\
    EvaluationCourses,EvaluationFellowsBackup, EvaluationCoursesBackup,LogEvaluadores,\
    LogApplications,evaluandocourses_table,evaluandofellows_table,FellowBackup,FellowDocumentsBackup,\
    FellowObjectivesBackup,FellowActivitiesBackup,Notifications,SaveFellow,SaveCourse#,CursoBackup,CourseObjectivesBackup,\
    #CourseCollaboratorsBackup,CourseBudgetsItemsBackup,DocumentosCursosBackup

from constants import IP , SUBJECT , DUMMY_MAIL , SUBJECT_RESEND,\
    ALLOWED_AVATAR_EXTENSIONS, ROLES ,PROJECT_ROOT, UPLOAD_FOLDER, ALLOWED_DOCUMENT_EXTENSIONS,\
    SUBJECT_INVITATION, SUBJECT_PASSWORD, IP_DOMAIN
from forms import CourseForm,FellowForm,BudgetForm,ObjectiveForm, ActivityForm,\
    MiniForm,MiniForm2 ,CollaboratorForm,FellowForm,LoginForm,RegisterForm,ForgotPasswordForm,\
    RecoverPasswordForm, MiniCourse, ObjectiveForm2, ModalRoleForm, ModalApprovedForm,ProbandoForm,\
    EditProfileForm

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.sql import func

import subprocess
import shlex

from flask import make_response

from threading import Thread
import pdfkit

import pickle

application = Flask(__name__)
application.config["SECRET_KEY"] = generate_key()
application.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER

# Inicializacion de las extensiones

## flask_login
from flask_login import login_user,login_required,logout_user,current_user,LoginManager
login_manager = LoginManager()

login_manager.login_view = "login"

login_session=dbSession()

@login_manager.user_loader
def load_user(id):

    ## creo una session global para cargar el usuario logueandose
    ## no modifico sus parametros es solo para cargarlo

    ## Global para  logout pueda usar esta session tambien

    user=login_session.query(User).get(id)

    return(user)


login_manager.init_app(application)

## Inicializacion de flask principal
principal=Principal(application)

admin_permission =Permission(RoleNeed('admin'))
estandar_permission =Permission(RoleNeed('estandar'))
asistentes_permission =Permission(RoleNeed('asistentes'))
evaluadores_permission =Permission(RoleNeed('evaluadores'))
ROLES={"1":"estandar","2":"evaluadores","3":"admin","4":"asistentes"}

## flask_mail
from flask_mail import Message, Mail

### Configuraciones
application.config["MAIL_SERVER"]= "smtp.gmail.com"
application.config["MAIL_PORT"]= 465
application.config["MAIL_USE_SSL"]= True
application.config["MAIL_USERNAME"]= "prueba.biolac@gmail.com"
application.config["MAIL_PASSWORD"]= "maracaibo2"
application.config["FROM_ADDR"]="biolac.prueba@gmail.com"
TO_ADDR=[""]

### Inicializacion de la extension
mail = Mail(application)

def send_async_email(app, msg):
    with application.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients,html):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = html
    thr = Thread(target=send_async_email, args=[application, msg])
    thr.start()

## current_user to js
from flask_jsglue import JSGlue
jsglue = JSGlue(application)

## flask ksocketio
#from flask_socketio import SocketIO
#socketio = SocketIO()

## modulo Its Dangerous
from itsdangerous import URLSafeTimedSerializer,URLSafeSerializer
ts=URLSafeTimedSerializer(application.config["SECRET_KEY"])
serializer=URLSafeSerializer("xvfsdghyomlnkdjshwjeddlcosjego_zxcaq")

## Security on filenames
#from flask_bcrypt import Bcrypt
#bcrypt = Bcrypt(application)

## manager
from flask_script import Manager
manager = Manager(application)
####  Finalizacion de la inicializacion de las extensiones

#### Utils function
def saving_files(fellow_document):

    """ Funcion para cargar los arhibos subidos en el filesystem
    request: Esta variable es el objeto obtenido de request.form['file']"""

    path=""
    realFileName=""
    dummy_filename=""
    if fellow_document.filename =='':
        file_path="No hay ningun archivo"
        return(file_path,realFileName,dummy_filename)

    else:
        if fellow_document and _allowed_file(fellow_document.filename,ALLOWED_DOCUMENT_EXTENSIONS):

            name_doc= "." in fellow_document.filename and fellow_document.filename.rsplit('.',1)[0]
            doc_ext= "." in fellow_document.filename and fellow_document.filename.rsplit('.',1)[1]

            ## Renombro el archivo con el id del usuario actual
            realFileName = name_doc + str("_user_") + str(current_user.id)+ doc_ext

            ## Guardo el archivo en el filesystem con el  hash del nombre
            #fellow_document.filename=str(bcrypt.generate_password_hash(realFileName))

            ## Guardo el archivo en el filesystem
            filename = secure_filename(fellow_document.filename)

            if not os.path.exists(application.config['UPLOAD_FOLDER']):
                make_dir(application.config['UPLOAD_FOLDER'])

            else:
                if not os.path.exists(os.path.join(application.config['UPLOAD_FOLDER'],str(current_user.id))):
                    make_dir_user_folder(application.config['UPLOAD_FOLDER'],str(current_user.id))
                else:
                    pass
            path=os.path.join(application.config['UPLOAD_FOLDER'],str(current_user.id),filename)

            ## linea original de la funcion
            #path=os.path.join(application.config['UPLOAD_FOLDER'], filename)
            try:
                fellow_document.save(os.path.join(application.config['UPLOAD_FOLDER'],str(current_user.id), filename))
                return(path,realFileName,fellow_document.filename)
            except Exception as e:
                return("Ocurrio un error" + str(e))


#Endpoints & URLs

@application.route("/registro", methods=["GET","POST"])
def registro():

    """ Registro del usuario en la plataforma de biolac"""

    ##  No es lo mejor per oes como puedo resolver dado que no tengo el context
    ## de la app y estos plugins no los puedo inicializar dentro del factory

    ## para encriptacion de los correos enviados al usuario
    #ts=URLSafeTimedSerializer(app.config["SECRET_KEY"])

    ##  Comienzo del registro
    form=RegisterForm()

    if request.method=="POST" and form.validate_on_submit():


        email=request.form['email']
        password=request.form['password']
        re_password=request.form['re_password']
        name=request.form['name']
        lastname=request.form['lastname']
        birth_date=request.form['birth_date']
        citizenship=request.form['citizenship']
        gender=request.form['gender']
        marital_status=request.form['marital_status']
        country=request.form['country']
        city=request.form['city']
        zip_code=request.form['zip_code']
        address=request.form['address']
        phonenumber=request.form['phonenumber']
        cellphone=request.form['cellphone']
        institution=request.form['institution']
        faculty=request.form['faculty']
        section=request.form['section']
        max_academic_level=request.form['max_academic_level']
        current_academic_level=request.form['current_academic_level']
        work_place=request.form['work_place']
        mentor=request.form['mentor']
        mentor_mail=request.form['mentor_mail']

        ## chequeo si el usuario no existe en el sistema
        with session_manager() as session:

            user=session.query(User).filter_by(email=email).first()

            if user is None:
                pass
            else:
                flash("El usuario ya esta registrado en el sistema",'already')
                return render_template("register_form.html",form=form)

        ##validacion de si hay un archivo en el filesystem
        path=''
        profile_picture=request.files['profile_picture']

        user=User(email,password,name,lastname,birth_date,citizenship,gender,\
        marital_status,country,city,zip_code,address,institution,\
        faculty,section,max_academic_level,current_academic_level,work_place,\
        cellphone,phonenumber,profile_picture="",mentor=mentor,mentor_mail=mentor_mail)


        with session_manager() as session:

            role=session.query(Role).get(1)
            try:
                role.users.append(user)
            except Exception as e:
                return(str(e))

            session.add(user)
            session.flush()

            u=session.query(User).filter_by(email=email).first()
            token_id=serializer.dumps(str(u.id),salt="passing_id")
            u.token=token_id

            #session.flush()
            #session.add(u)

            if profile_picture.filename =='':
                ## opcion para agregar una foto de perfil
                profile_path="images/default.jpg"

            ## Validacion de los archivos y la foto de perfil de  los postulantes
            else:
                if profile_picture and _allowed_file(profile_picture.filename,ALLOWED_AVATAR_EXTENSIONS):
                    filename = secure_filename(profile_picture.filename)

                    if not os.path.exists(application.config['UPLOAD_FOLDER']):
                        make_dir(application.config['UPLOAD_FOLDER'])

                    else:
                        if not os.path.exists(os.path.join(application.config['UPLOAD_FOLDER'],str(u.id))):
                            make_dir_user_folder(application.config['UPLOAD_FOLDER'],str(u.id))
                        else:
                            pass
                    path=os.path.join(application.config['UPLOAD_FOLDER'],str(u.id),filename)
                    try:
                        profile_picture.save(os.path.join(application.config['UPLOAD_FOLDER'],str(u.id), filename))
                        profile_path="uploads"+"/"+str(u.id)+"/"+str(filename)
                    except Exception as e:
                        return("Ocurrio un error" + str(e))


            u.profile_picture=profile_path
            session.add(u)

        try:
            token_mail = ts.dumps(email, salt='email-confirmation')

        except Exception as e:
            ## Algun error para la funcion e imprime el error

            return(str(e))

        ## Genero el url con el token necesario (RED LOCAL)

        #confirm_url = url_for( 'validation', token=token,_external=True)
        confirm_url2=IP_DOMAIN+"/validation/"+str(token_mail)

        ## Hago una plantilla con jinja que la cual tendra el contenido del correo
        html=render_template('_activation_mail.html',confirm_url=confirm_url2)

        ## Anexando la informacion al correo especificado

        #send_email(subject, sender, recipients,html, html_body):
        send_email(SUBJECT,application.config["MAIL_USERNAME"],[email],html)

        #msg = Message(SUBJECT, sender=application.config["MAIL_USERNAME"], recipients=['cristhian2bravo@gmail.com'])
        #msg.body = html
        #mail.send(msg)

        ##send_correo() ## enia el correo
        #Esto me permite validarlo offline (debo hacer funcion que mande correo)
        #return(str(html))

        return render_template("validation_info.html",data={"nombre":name,"id":email,"flag_reenviado":False})
        ############################################
        #debo poner validacion de si el usuario ya esta registrado en la plataforma

    else:

        flash("Hay errores en la forma que llenaste. Intentalo de nuevo")
        return render_template("register_form.html",form=form)


@application.route("/validation/<token>")
def account_validation(token):

    """ Maneja el proceso de comprobacion del token para la validacion del
    usuario en la plataforma de biolac """

    try:
        email = ts.loads(token, salt="email-confirmation", max_age=18000)
    except Exception as e:
        print(e)
        return(str(e))

    with session_manager() as session:
        user=session.query(User).filter_by(email=email).first()
        if user:
            user.active=True
            session.add(user)
        else:
            error_msg="No hay ningun usuario registrado con ese nombre"
            return render_template("error_form.html",error=error_msg)

    return render_template("validation_success.html")


@application.route("/resend/<id>")
def resend(id):

    try:
        token = ts.dumps(id, salt='email-confirmation')

    except Exception as e:
        ## Algun error para la funcion e imprime el error
        return(str(e))



    ## Genero el url con el token necesario (RED LOCAL)

    #confirm_url = url_for( 'validation', token=token,_external=True)
    confirm_url=IP_DOMAIN+"/validation/"+str(token)

    ## Hago una plantilla con jinja que la cual tendra el contenido del correo
    html=render_template('_activation_mail.html',confirm_url=confirm_url)

    ## Anexando la informacion al correo especificado
    send_email(SUBJECT_RESEND,application.config["MAIL_USERNAME"],[id],html)

    # msg = Message(SUBJECT_RESEND, sender=application.config["MAIL_USERNAME"], recipients=[id])
    # msg.body = html
    # mail.send(msg)
    ##send_correo() ## enia el correo
    #Esto me permite validarlo offline (debo hacer funcion que mande correo)
    #return(str(html))

    return render_template("validation_info.html",data={"flag_reenviado":True})


@application.route("/login", methods=["GET","POST"])
def login():

    ## Tristemente debo volver a romper el dry para inicializar flask principal
    form=LoginForm()


    ## Validacion de las formas
    if request.method=="POST" and form.validate_on_submit():

        if current_user.is_authenticated:

            print(current_user.name)

            logout_user()

            login_session.close()

            # Remove session keys set by Flask-Principal
            for key in ('identity.name', 'identity.auth_type'):
                s.pop(key, None)

            # Tell Flask-Principal the user is anonymous
            identity_changed.send(current_app._get_current_object(),
                                  identity=AnonymousIdentity())

        email=request.form['email']
        password=request.form['password']

        ## Logica para poder usar el boolean field del form
        if "remember_me" not in request.form:

            remember_option=False

        else:
            remember_option=True


        ## Manejo de las conexiones de la base de datos
        with session_manager() as session:

            user=session.query(User).filter_by(email=email).first()


            if user:

                if user.is_active():
                    if user.check_password(password):

                        login_user(user,remember=remember_option)

                        try:
                            s['rol']=user.role_id
                            s['id']=user.id
                            s['name']=user.name

                        except Exception as e:

                            return("Ocurrio un error " + str(e))

                        role=ROLES[str(user.role_id)]

                        ## Setting up flask_principal
                        identity_changed.send(current_app._get_current_object(),\
                            identity=Identity(user.id))

                        next=request.args.get('next')

                        if not next_is_valid(next,role):

                            return("probando que next funciona")

                        if role == 'admin':
                            return redirect(next or url_for('dashboard'))

                        else:

                            return redirect(next or url_for('home'))
                    else:

                        return("La clave proporcionada es incorrecta")
                else:
                    return("""El usuario no esta activo en la plataforma.
                    Si no recibiste el correo de validacion sigue el siguiente
                    link para reenviarlo""")
            else:
                return("El usuario no se encuentra registrado en la plataforma")

    else:
        return render_template("login_form.html",form=form)

@application.route("/logout")
@login_required
def logout():
    logout_user()

    ## cierro la session de la base de datos
    login_session.close()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        s.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for("login"))

## logica para la recuperacion del password aunque esto es en el blueprint_login

@application.route("/forgot_password", methods=["GET","POST"])
def forgot_password():


    form=ForgotPasswordForm()

    if request.method=="POST" and form.validate_on_submit():

        ##"Nueva destruccion del dry "
        correo= request.form['email']

        with session_manager() as session:

            user=session.query(User).filter_by(email=correo).first()

            if user:

                try:
                    token = ts.dumps( correo, salt='forgot_password_recovery')

                except Exception as e:
                    ## Algun error para la funcion e imprime el error
                    return(str(e))

                #confirm_url = url_for( 'validation', token=token,_external=True)
                confirm_url=IP_DOMAIN+"/new_password_validation/"+str(token)

                ## Hago una plantilla con jinja que la cual tendra el contenido
                #del correo
                html=render_template('_forgot_password_mail.html',\
                    confirm_url=confirm_url)

                ## Anexando la informacion al correo especificado
                send_email(SUBJECT_PASSWORD,application.config["MAIL_USERNAME"],[correo],html)

                # msg = Message(SUBJECT_PASSWORD, \
                #     sender=application.config["MAIL_USERNAME"], recipients=[correo])
                # msg.body = html
                # mail.send(msg)

                return render_template("forgot_password_info.html",\
                    data={"id":correo})

            else:
                flash("No hay ningun usuario asociado a esa cuenta de correo","error_password")
                return render_template("forgot_password_form.html",form=form)

    else:
        return render_template("forgot_password_form.html",form=form)


@application.route("/new_password_validation/<token>")
def new_password_validation(token):

    """Maneja el proceso de comporobacion del token enviado al correo
    para verificar que el usuario con ese correo en el sistema efectivamente
    entró a su correo y esta solicitando el cambio"""

    email=''

    try:
        email = ts.loads(token, salt="forgot_password_recovery", max_age=18000)
    except Exception as e:
        print(e)

    ## Obtengo el usuario dependiendo del email si  el usuario existe
    ## redirijo a la pagina que muestra la forma de reset password
    with session_manager() as session:
        user=session.query(User).filter_by(email=email).first()
        if user:
            return redirect(url_for('new_password',user_id=user.id))
        else:
            msg="Ese usuario no esta registrado en la plataforma UNU-BIOLAC"
            return render_template("error_password_recovery.html",error=msg)


@application.route("/new_password/<user_id>",methods=["GET","POST"])
def new_password(user_id):

    """ Forma para el proceso de recuperacion del password desde la base
    de datos """

    form= RecoverPasswordForm()

    if request.method=="POST" and form.validate_on_submit():

        new_password=request.form['password']
        new_password_verification=request.form['re_password']

        new_password=generate_password_hash(new_password)

        with session_manager() as session:
            user=session.query(User).filter(User.id==user_id).update({User.password:new_password})
            return render_template("password_changed.html")

    else:
        return render_template("recover_password_form.html", data={"form":form,"user":user_id})
#
#
#
@application.route("/home")
@login_required
def home():

    with session_manager() as session:

        print(current_user.name)

        pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        print(str(pending_fellow))
        pending=pending_fellow+pending_courses


    return render_template("home.html",avatar_url= current_user.profile_picture, user_level=current_user.role_id,name=current_user.name, pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})
#
#
# ## Utility function
# @identity_loaded.connect_via(application)
# def on_identity_loaded(sender, identity):
#
#     """
#     Esta funcion es utilizada para cargar en el request_context actual
#     algunas creedenciales y atributos del usuario que se esta conectando
#     al sistema/
#
#     En algunos bluerpints tenemos decoradores y views que se encargan de
#     enviar señales a este modulo  con el app context donde se este corriendo
#     para verificar si los usuarios tienen ciertos atributos pero para hacer
#     la verificacion se deben tener dichos atributos cargados. Por lo cual
#     esos modulos envian su app_context atraves del decorador
#     @identity_loaded.connect_via(). Luego al recibir el contexto y la
#     identidad del usuario se hace un querie a la base de datos para obtener
#     al mencionado usuario y se lo asigna al objeto g de flask el cual esta
#     atado al current application context y al hacerlo con la funcion
#     identity.provides agregamos a los objetos que necesitamos de flask
#     principal a nuestro current user y podemos usar todo las demas
#     funcionalidades del modulo.
#
#     """
#
#     if identity.id != None:
#
#         identity.user=current_user
#
#         ## Add the userNeed to the identity
#         if hasattr(current_user,'id'):
#
#             identity.provides.add(UserNeed(current_user.id))
#
#         ## Assuming the User model has a list of roles, update the
#         # identity with the roles that the user provides
#
#         if hasattr(current_user,'role_id'):
#
#             identity.provides.add(RoleNeed(ROLES[str(current_user.role_id)]))
#     else:
#
#         for key in ('identity.name','identity.auth_type','user'):
#                 s.pop(key,None)



@application.route("/Apply/Courses",methods=["POST","GET"])
@login_required
def apply_courses():



    if request.method=="GET":

        with session_manager() as session:

            if current_user.role_id==2:

                pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
                pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
                pending=pending_fellow+pending_courses
                pending_union={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow}

            else:

                pending_union={}

            ## Query del save fellow de la tabla SaveFellow
            data=session.query(SaveCourse).filter_by(user_id=current_user.id).first()

            if data:


                budget_keys=[]
                budget_keys_num=[]

                objectives_keys=[]
                objectives_keys_num=[]

                collaborators_keys=[]
                collaborators_keys_num=[]

                other_keys=[]

                budget=[]
                budget_backup=[]

                objectives=[]
                objectives_backup=[]

                collaborators=[]
                collaborators_backup=[]

                other=[]

                for key in data.data:


                    if key.startswith('courseObjectives-'):

                        objectives_keys.append(key)
                        value=re.search(r'\d+', key).group()
                        if value not in objectives_keys_num:
                            objectives_keys_num.append(value)

                        # print(objectives_keys_num)
                        # co=CourseObjectives(data.data[key])
                        # objectives.append(co)
                        #return(str(objectives))

                    elif key.startswith('courseBudgetItems-'):

                        budget_keys.append(key)
                        value=re.search(r'\d+', key).group()
                        if value not in budget_keys_num:
                            budget_keys_num.append(value)
                        # bo=CourseBudgetsItems(data.data[key])
                        # budget.append(bo)


                    elif key.startswith('courseCollaborators-'):

                        collaborators_keys.append(key)
                        value=re.search(r'\d+', key).group()
                        if value not in collaborators_keys_num:
                            collaborators_keys_num.append(value)
                        # coll=CourseCollaborators(data.data[key])
                        # collaborators.append(coll)


                    else:

                        other_keys.append(key)
                        other.append(data.data[key])

                ## Agrupo las llaves del mismo formulario dinamico en un solo
                ## sub arreglos que para poder parsear los datos mejor.
                for i in range(len(objectives_keys_num)):

                    subkeys=[]
                    for key in objectives_keys:

                        if int(re.search(r'\d+', key).group()) == i:

                            subkeys.append(key)

                    objectives_backup.append(subkeys)


                # Aqui creo el arreglo de objetos que necesito para pasar a la clase
                for arreglo in objectives_backup:

                    arreglo=sorted(arreglo)
                    co=CourseObjectives()
                    co.objective_item=data.data[arreglo[0]]
                    objectives.append(co)


                ## Despues de definir cuantos bloques dinamicos hay me encargo de separar
                ## cada bloque en un subarray de manera que sea facil inicializar
                ## la clase

                for i in range(len(budget_keys_num)):

                    subkeys=[]
                    for key in budget_keys:

                        if int(re.search(r'\d+', key).group()) == i:

                            subkeys.append(key)

                    budget_backup.append(subkeys)

                ## Aqui creo el arreglo de objetos que necesito para pasar a la clase
                for arreglo in budget_backup:

                    arreglo=sorted(arreglo)
                    co=CourseBudgetsItems()
                    co.budget_desc=data.data[arreglo[0]]
                    co.budget_value=data.data[arreglo[1]]
                    budget.append(co)


                ## Hago lo mismo para los colaboradores

                for i in range(len(collaborators_keys_num)):

                    subkeys=[]
                    for key in collaborators_keys:

                        if int(re.search(r'\d+', key).group()) == i:

                            subkeys.append(key)

                    collaborators_backup.append(subkeys)


                print(collaborators_backup)

                ## Aqui creo el arreglo de objetos que necesito para pasar a la clase
                i=0

                for arreglo in collaborators_backup:


                    arreglo=sorted(arreglo)
                    arreglo.insert(1,"CourseCollaborators-"+str(i)+"-coll_cv")

                    co=CourseCollaborators()
                    co.coll_name=data.data[arreglo[4]]
                    co.coll_position=data.data[arreglo[6]]
                    co.coll_institution=data.data[arreglo[3]]
                    co.coll_phone=data.data[arreglo[5]]
                    co.coll_email=data.data[arreglo[2]]
                    co.coll_area=data.data[arreglo[0]]

                    # # budget.append(co)
                    collaborators.append(co)
                    i+=1

                i=0

                c1=Curso()

                if len(c1.courseObjectives) == 0:
                    c1.courseObjectives = objectives

                if len(c1.courseBudgetItems) == 0:
                    c1.courseBudgetItems = budget

                if len(c1.courseCollaborators) == 0:
                    c1.courseCollaborators = collaborators


                c1.courseTitle=data.data['courseTitle']


                if "priority" in data.data:

                    c1.priority=data.data['priority']
                else:
                    pass

                #c1.priority=data.data['priority']
                c1.hostName=data.data['hostName']
                c1.destination=data.data['destination']
                c1.hostAddress=data.data['hostAddress']
                c1.coordName=data.data['coordName']
                c1.coordTitle=data.data['coordTitle']
                c1.coordAffiliation=data.data['coordAffiliation']

                if data.data["commDate"]=="":
                    pass

                else:
                    c1.commDate=datetime.datetime.strptime(data.data['commDate'],'%Y-%m-%d')


                if data.data["termDate"]=="":
                    pass

                else:
                    c1.termDate=datetime.datetime.strptime(data.data['termDate'],'%Y-%m-%d')

                #c1.commDate=datetime.datetime.strptime(data.data['commDate'], '%Y-%m-%d')
                #c1.termDate=datetime.datetime.strptime(data.data['termDate'], '%Y-%m-%d')

                c1.courseDescription=data.data['courseDescription']
                c1.organizationTrainingDescription=data.data['organizationTrainingDescription']
                c1.courseTrainees=data.data['courseTrainees']
                c1.fundingSource=data.data['fundingSource']
                c1.fundingSourceScore=data.data['fundingSourceScore']
                c1.counterpartFund=data.data['counterpartFund']
                c1.counterpartFundScore=data.data['counterpartFundScore']

                form= CourseForm(obj=c1)


                # avatar="Hola"
                # user_level="2"
                # pending={"asignments":"bla","asigned_courses":"bla2","asigned_fellows":"bla3"}
                # user={"token":"bla","name":"bla"}


                return render_template("course_form.html",avatar_url=current_user.profile_picture,\
                user_level = current_user.role_id,form=form, \
                user={"token":current_user.token,"name":current_user.name},\
                pending=pending_union)

            else:

                c1=Curso()

                if len(c1.courseObjectives) == 0:
                    c1.courseObjectives = [CourseObjectives()]

                if len(c1.courseBudgetItems) == 0:
                    c1.courseBudgetItems = [CourseBudgetItems()]

                if len(c1.courseCollaborators) == 0:
                    c1.courseCollaborators = [CourseCollaborators()]


                form= CourseForm(obj=c1)

                return render_template("course_form.html",avatar_url=current_user.profile_picture,\
                user_level = current_user.role_id,form=form, \
                user={"token":current_user.token,"name":current_user.name},\
                pending=pending_union)



    if request.method=="POST": #and form.validate_on_submit():

        c1=Curso()

        if len(c1.courseObjectives) == 0:
            c1.courseObjectives = [CourseObjectives()]

        if len(c1.courseBudgetItems) == 0:
            c1.courseBudgetItems = [CourseBudgetsItems()]

        if len(c1.courseCollaborators) == 0:
            c1.courseCollaborators = [CourseCollaborators()]

        form=CourseForm(obj=c1)

        data=request.form

        print(data)

        file_dict={}
        i=1

        for archivo in request.files:

            path,realFilename,hashed_name=saving_files(request.files[archivo])
            file_dict['doc_curso'+str(i)]=[path,realFilename,hashed_name]
            i+=1


        for j in range(1,i):
            doc=DocumentosCursos(file_dict["doc_curso"+str(j)][1],\
                file_dict["doc_curso"+str(j)][0],\
                file_dict["doc_curso"+str(j)][2])
            c1.cursoDocs.append(doc)
            c1.courseCollaborators.coll_cv=file_dict["doc_curso"+str(j)][0]


        form.populate_obj(c1)

        with session_manager() as session:

            ### Agrego los campos criticos para el flujo de la aplicacion
            c1.user_candidateEmail=current_user.email
            c1.user_candidateId=current_user.token
            c1.user_candidateName=current_user.name
            c1.user_candidateLastName=current_user.lastname

            ## Agrego a el usuario postulante a el usuario
            u=session.query(User).get(current_user.id)

            u.curso.append(c1)

            session.add(c1)

            try:
                session.flush()
            except Exception as e:

                return("Ocurrio un error mientras hacia el flush", +str(e))

            log=LogApplications(c1.hostAddress,current_user.id,"Course",c1.courseTitle,current_user.email,current_user.id)
            session.add(log)

            noti=Notifications("Postulacion Curso","El usuario "+str(current_user.name)+\
            " " + str(current_user.email)+" Postulo un curso",\
            datetime.datetime.now(),"postulacion_curso")

            administrador=session.query(User).get(2)
            administrador.notifications.append(noti)

            saved_data=session.query(SaveCourse).filter_by(user_id=current_user.id)
            saved_data.delete()

            session.add(noti)

        return redirect(url_for('courses_application'))

    # else:
    #
    #     with session_manager() as session:
    #
    #         pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
    #         pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
    #         print(str(pending_fellow))
    #         pending=pending_fellow+pending_courses
    #
    #     return render_template("course_form.html",avatar_url=current_user.profile_picture,user_level = current_user.role_id,form=form, user={"token":current_user.token,"name":current_user.name},\
    #     pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})
    #return render_template('course_form.html',user_level = current_user.role_id,form=form)

@application.route("/Apply/Fellow", methods=["GET","POST"])
def apply_fellow():


    form= FellowForm()

    if request.method=="GET":

        with session_manager() as session:

            if current_user.role_id==2:

                pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
                pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
                pending=pending_fellow+pending_courses
                pending_union={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow}

            else:

                pending_union={}

            data=session.query(SaveFellow).filter_by(user_id=current_user.id).first()

            if data:

                activities_keys=[]
                objectives_keys=[]
                other_keys=[]

                activities=[]
                objectives=[]
                other=[]


                for key in data.data:

                    if key.startswith('fellowObjectives-'):

                        objectives_keys.append(key)
                        fo=FellowObjectives(data.data[key])
                        objectives.append(fo)
                        #return(str(objectives))

                    elif key.startswith('fellowActivities-'):

                        activities_keys.append(key)
                        ao=FellowActivities(data.data[key])
                        activities.append(ao)
                    else:

                        other_keys.append(key)
                        other.append(data.data[key])


                f1=Fellow()

                if len(f1.fellowObjectives) == 0:
                    #f1.fellowObjectives = [FellowObjectives()]
                    f1.fellowObjectives = objectives


                if len(f1.fellowActivities) == 0:
                    #f1.fellowActivities = [FellowActivities()]
                    f1.fellowActivities = activities


                print(data)


                f1.fellowTitle=data.data['fellowTitle']


                if "priority" in data.data:

                    f1.priority=data.data['priority']
                else:
                    pass

                f1.destination=data.data['destination']
                f1.generalObjective=data.data['generalObjective']
                f1.justification=data.data['justification']
                f1.methodology=data.data['methodology']
                f1.workingPlan=data.data['workingPlan']
                f1.criteria=data.data['criteria']

                if data.data["commDate"]=="":
                    pass

                else:
                    f1.commDate=datetime.datetime.strptime(data.data['commDate'],'%Y-%m-%d')


                    if data.data["termDate"]=="":
                        pass

                    else:
                        f1.termDate=datetime.datetime.strptime(data.data['termDate'],'%Y-%m-%d')

                # f1.termDate=datetime.datetime.strptime(data.data['termDate'],'%Y-%m-%d')
                f1.hostInstitution=data.data['hostInstitution']

                form= FellowForm(obj=f1)


                return render_template('fellow_form.html', avatar_url=current_user.profile_picture,\
                user_level=current_user.role_id, form = form,user={"token":current_user.token,"name":current_user.name},\
                pending=pending_union)

                #return render_template("blob_fellow.html",form=form, user=user)

            else:

                f1=Fellow()

                if len(f1.fellowObjectives) == 0:
                    f1.fellowObjectives = [FellowObjectives()]


                if len(f1.fellowActivities) == 0:
                    f1.fellowActivities = [FellowActivities()]

                form= FellowForm(obj=f1)

                return render_template('fellow_form.html', avatar_url=current_user.profile_picture,\
                user_level=current_user.role_id, form = form,user={"token":current_user.token,"name":current_user.name},\
                pending=pending_union)


    if request.method=="POST": #and form.validate_on_submit():



        f1=Fellow()

        if len(f1.fellowObjectives) == 0:
            f1.fellowObjectives = [FellowObjectives()]

        if len(f1.fellowActivities) == 0:
            f1.fellowActivities = [FellowActivities()]

        form= FellowForm(obj=f1)

        try:
            ## Debo asegurarme con el cliente si los archivos pueden ir vacios
            ## o todos son obligatorios
            path,realFileName,hashed_name=saving_files(request.files['acceptanceLetter'])
            path1,realFileName1,hashed_name1=saving_files(request.files['fellowCV'])
            path2,realFileName2,hashed_name2=saving_files(request.files['mentorCV'])
            path3,realFileName3,hashed_name3=saving_files(request.files['recommendationLetter'])
            path4,realFileName4,hashed_name4=saving_files(request.files['infoForm'])
            path5,realFileName5,hashed_name5=saving_files(request.files['photo'])
            path6,realFileName6,hashed_name6=saving_files(request.files['vendorForm'])
            path7,realFileName7,hashed_name7=saving_files(request.files['fafDoc6'])
            path8,realFileName8,hashed_name8=saving_files(request.files['fafDoc7'])
            path9,realFileName9,hashed_name9=saving_files(request.files['medicalInform'])

        except Exception as e:
            return("Ocurrio un error" +str(e))

        f1.id=current_user.id
        f1.name=current_user.name
        f1.lastName=current_user.lastname
        f1.citizenship=current_user.citizenship
        f1.mentor_p=current_user.mentor
        f1.mentor_pEmail=current_user.mentor_mail
        f1.fellow_userTokenId=current_user.token
        f1.fellow_candidateEmail=current_user.email
        form.populate_obj(f1)

        doc=FellowDocuments(realFileName,path,hashed_name)
        doc1=FellowDocuments(realFileName1,path1,hashed_name1)
        doc2=FellowDocuments(realFileName2,path2,hashed_name2)
        doc3=FellowDocuments(realFileName3,path3,hashed_name3)
        doc4=FellowDocuments(realFileName4,path4,hashed_name4)
        doc5=FellowDocuments(realFileName5,path5,hashed_name5)
        doc6=FellowDocuments(realFileName6,path6,hashed_name6)
        doc7=FellowDocuments(realFileName7,path7,hashed_name7)
        doc8=FellowDocuments(realFileName8,path8,hashed_name8)
        doc9=FellowDocuments(realFileName9,path9,hashed_name9)

        f1.fellowDocs.append(doc)
        f1.fellowDocs.append(doc1)
        f1.fellowDocs.append(doc2)
        f1.fellowDocs.append(doc3)
        f1.fellowDocs.append(doc4)
        f1.fellowDocs.append(doc5)
        f1.fellowDocs.append(doc6)
        f1.fellowDocs.append(doc7)
        f1.fellowDocs.append(doc8)
        f1.fellowDocs.append(doc9)

        log=LogApplications(f1.name,current_user.id,"Fellow",f1.fellowTitle,current_user.email,current_user.id)

        noti=Notifications("Postulacion Fellow","El usuario "+str(current_user.name)+\
        " " + str(current_user.email)+" Postulo un fellow",\
        datetime.datetime.now(),"Postulo un fellow")

        print("LLegue al final de session manager")

        with session_manager() as session:

            administrador=session.query(User).get(2)
            administrador.notifications.append(noti)

            saved_data=session.query(SaveFellow).filter_by(user_id=current_user.id)
            saved_data.delete()

            session.add(f1)
            session.add(log)
            session.add(noti)

        return redirect(url_for('fellow_application'))
        return("Todo ok")


@application.route("/Applications/Fellow")
@login_required
def fellow_application():

    fellows = []

    with session_manager() as session:

        if  current_user.role_id == 1:

            data=session.query(User,Fellow).join(Fellow, Fellow.id==User.id).filter(Fellow.id==current_user.id).first()

            if data:
                d=data
                fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                institution=d[0].institution,citizenship=d[0].citizenship,evaluations=d[1].revisiones_completadas,
                status=d[1].status_aprobado,place=d[1].destination,\
                token=d[0].token)
                fellows.append(fellow)

            else:
                return render_template('fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellows_list = fellows)


        elif  current_user.role_id== 2:

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses

            data=session.query(User,Fellow).join(Fellow, Fellow.id==User.id).filter(Fellow.id==current_user.id).first()

            if data:
                d=data
                fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                institution=d[0].institution,citizenship=d[0].citizenship,evaluations=d[1].revisiones_completadas,
                status=d[1].status_aprobado,place=d[1].destination,\
                token=d[0].token)
                fellows.append(fellow)
                return render_template('fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellows_list = fellows,pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

            else:
                return render_template('fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellows_list = fellows,pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

        else:

            data=session.query(User,Fellow).join(Fellow,User.id==Fellow.id).filter(Fellow.id==User.id)

            if data:

                for d in data:
                    fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                    institution=d[0].institution,citizenship=d[0].citizenship,evaluations=d[1].revisiones_completadas,
                    status=d[1].status_aprobado,place=d[1].destination,\
                    token=d[0].token,hostInstitution=d[1].hostInstitution,mentor=d[1].mentor_p,mentor_mail=d[1].mentor_pEmail,\
                    commDate=d[1].commDate,termDate=d[1].termDate)
                    fellows.append(fellow)

            else:
                return render_template('fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellows_list = fellows)

    return render_template('fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellows_list = fellows)

@application.route("/Applications/Fellow/Info/<token>", methods=["GET","POST"])
@login_required
def fellow_info(token):

    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    if  current_user.role_id == 1:

        with session_manager() as session:

            fellows=[]

            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            data=session.query(User,Fellow).join(Fellow, Fellow.id==User.id).filter(Fellow.id==current_user.id).first()
            fellow_objectives=session.query(FellowObjectives).filter(FellowObjectives.fellow_id==current_user.id).all()
            fellow_activities=session.query(FellowActivities).filter(FellowActivities.fellow_id==current_user.id).all()


            if data:
                d=data
                fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                institution=d[0].institution,generalObjective=d[1].generalObjective,justification=d[1].justification,plan=d[1].workingPlan,\
                citizenship=d[0].citizenship,evaluations=d[1].revisiones_completadas, methodology=d[1].methodology,\
                status=d[1].status_aprobado,priority=d[1].priority,destination=d[1].destination,\
                token=d[0].token,objectives=fellow_objectives,activities=fellow_activities,id=d[1].id)
                return render_template('application_fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellow =fellow,user={"token":current_user.token,"name":current_user.name},\
                annex=annex)

            else:
                return("No lograste entrar en data ")


    elif current_user.role_id== 2:

        with session_manager() as session:

            fellows=[]

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses

            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            data=session.query(User,Fellow).join(Fellow, Fellow.id==User.id).filter(Fellow.id==user_id).first()
            fellow_objectives=session.query(FellowObjectives).filter(FellowObjectives.fellow_id==user_id).all()
            fellow_activities=session.query(FellowActivities).filter(FellowActivities.fellow_id==user_id).all()
            evaluations=session.query(EvaluationFellows).filter_by(fellow_id=user_id,evaluator_id=current_user.id).all()


            if data:
                d=data
                fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                institution=d[0].institution,generalObjective=d[1].generalObjective,justification=d[1].justification,plan=d[1].workingPlan,\
                citizenship=d[0].citizenship,evaluations=evaluations, methodology=d[1].methodology,\
                status=d[1].status_aprobado,destination=d[1].destination,\
                token=d[0].token,objectives=fellow_objectives,priority=d[1].priority,activities=fellow_activities,\
                id=d[1].id)

                return render_template('application_fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellow =fellow,user={"token":current_user.token,"name":current_user.name},\
                annex=annex,pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

            else:
                return("No lograste entrar en data ")

    else:

        with session_manager() as session:

            fellows=[]



            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            data=session.query(User,Fellow).join(Fellow, Fellow.id==User.id).filter(Fellow.id==user_id).first()
            fellow_objectives=session.query(FellowObjectives).filter(FellowObjectives.fellow_id==user_id).all()
            ##aqui debo arreglar la data del querie para hacer la validacion de las evaluaciones
            fellow_activities=session.query(FellowActivities).filter(FellowActivities.fellow_id==user_id).all()
            evaluations=session.query(EvaluationFellows).filter_by(fellow_id=user_id).all()
            if data:

                d=data
                fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                institution=d[0].institution,generalObjective=d[1].generalObjective,justification=d[1].justification,plan=d[1].workingPlan,\
                citizenship=d[0].citizenship,evaluations=evaluations, methodology=d[1].methodology,\
                status=d[1].status_aprobado,destination=d[1].destination,\
                token=d[0].token,priority=d[1].priority,\
                objectives=fellow_objectives,activities=fellow_activities,\
                criteria=d[1].criteria,mentor=d[1].mentor_p,\
                mentor_email=d[1].mentor_pEmail,hostInstitution=d[1].hostInstitution,
                commDate=d[1].commDate,termDate=d[1].termDate,id=d[1].id)
                print(fellow)
                return render_template('application_fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellow =fellow, user={"token":current_user.token,"name":current_user.name},annex=annex)

            else:
                return("No lograste entrar en data ")

            return render_template('application_fellow.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, fellow =fellow)


    #return(str(current_user.role_id))

        #return(str(fellow_info)) ## debo retornar application fellow info
    #return("Pagina de informacion de los postulantes")


@application.route("/Asign/Evaluator/<token>", methods=["GET","POST"])
@login_required
def asign_evaluator(token):

    ## conocer a que usuario le asignare un evaluador

    """ Tengo que hacer aqui una logica de validacion muy importante para
    evitar que se asignen evaluadores repetidos """
    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    if request.method=="POST":

        evaluators_asigned= request.form

        ## Filtro de los id de los evaluadores que se le asignaran a dicha evaluacion
        llaves=[]
        for key in evaluators_asigned.keys():
            if key !='dataTables-example_length' and key !='button':
                llaves.append(int(key))


        with session_manager() as session:

            fellow=session.query(Fellow).filter_by(id=user_id).first()

            ## Conseguir una manera mas eficiente para hacer esto
            for i in range(len(llaves)):

                user=session.query(User).get(llaves[i])
                user.evaluados.append(fellow)

        #return("Felicidades ya asignaste a los evaluadores a esta evaluacion")
        return redirect(url_for('asign_evaluator', token=token))

    else:

        with session_manager() as session:

            ## Obtengo los id de los usuarios que estan evaluando el fellow
            getting_id=session.query(evaluandofellows_table).filter_by(fellow_id=user_id)
            keys=[g.user_id for g in getting_id]

            ## Busco todos los evaluadores que no esten asignados a este fellow
            evaluators=session.query(User).filter(~User.id.in_(keys)).filter_by(role_id=2).all()
            return render_template('asign_evaluator.html',user_level=3,evaluators_list=evaluators)

@application.route("/Asign/Evaluator/Courses/<id>/<token>", methods=["GET","POST"])
@login_required
def asign_evaluator_courses(id,token):

    ## conocer a que usuario le asignare un evaluador

    """ Tengo que hacer aqui una logica de validacion muy importante para
    evitar que se asignen evaluadores repetidos """
    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    url_id=int(id)

    if request.method=="POST":

        evaluators_asigned= request.form

        ## Filtro de los id de los evaluadores que se le asignaran a dicha evaluacion
        llaves=[]
        for key in evaluators_asigned.keys():
            if key !='dataTables-example_length' and key !='button':
                llaves.append(int(key))


        with session_manager() as session:

            curso=session.query(Curso).filter_by(id=url_id).first()

            ## Conseguir una manera mas eficiente para hacer esto
            for i in range(len(llaves)):

                user=session.query(User).get(llaves[i])
                user.evaluando_courses.append(curso)

        # return("Felicidades ya asignaste a los evaluadores a esta evaluacion")
        return redirect(url_for('asign_evaluator_courses',id=url_id, token=token))

    else:

        with session_manager() as session:

            ## Obtengo los id de los usuarios que estan evaluando el fellow
            getting_id=session.query(evaluandocourses_table).filter_by(curso_id=url_id)
            keys=[g.user_id for g in getting_id]
            print(keys)
            ## Busco todos los evaluadores que no esten asignados a este curso
            evaluators=session.query(User).filter(~User.id.in_(keys)).filter_by(role_id=2).all()
            print(evaluators)
            return render_template('asign_evaluator_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,evaluators_list=evaluators)



### Super importante arreglar esto
@application.route("/Applications/Courses")
@login_required
def courses_application():

    courses = []

    try:
        token = ts.dumps(current_user.id, salt='passing_id')
    except Exception as e:
        return("Ocurrio un error: linea 917 " + str(e))

    with session_manager() as session:

        if  current_user.role_id == 1 or current_user.role_id== 2:

            ## Por ahora se resuelve le problema pero debo revisar que pasa

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses

            data=session.query(User,Curso).join(Curso).filter(Curso.postulanteCurso_id==current_user.id).all()


            if data:

                for d in data:

                    course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                    institution=d[1].hostName,destination=d[1].destination,evaluations=d[1].revisiones_completadas,\
                    requested=d[1].status_revisado,status=d[1].status_aprobado,place=d[1].hostAddress,\
                    token=d[0].token, id=d[1].id,commDate=d[1].commDate,termDate=d[1].termDate)
                    courses.append(course)

            else:
                return render_template('courses.html',avatar_url=current_user.profile_picture,user_level =current_user.role_id, courses_list = courses,\
                pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})
        else:

            data=session.query(User,Curso).join(Curso).filter(Curso.postulanteCurso_id==User.id).all()

            total_budget= session.query(func.sum(CourseBudgetsItems.budget_value).label('suma')).scalar()

            if data:
                for d in data:

                    #suma= session.query(func.sum(CourseBudgetsItems.budget_value)).filter(CourseBudgetsItems.curso_id==d[1].id).scalar()
                    print(data)
                    course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                    institution=d[1].hostName,evaluations=str(d[1].revisiones_completadas) +"/5",
                    status=d[1].status_aprobado,place=d[1].hostAddress,destination=d[1].destination,\
                    token=d[0].token,id=d[1].id,requested=d[1].fundingSourceScore,approved= d[1].aprove_budget,coordName=d[1].coordName)
                    courses.append(course)


            else:
                return render_template('courses.html',avatar_url=current_user.profile_picture,user_level =current_user.role_id, courses_list = courses)

    ## Arreglar este template pero primero debo arreglar la base de datos
    return render_template('courses.html',avatar_url=current_user.profile_picture,user_level =current_user.role_id, courses_list = courses)


@application.route("/Applications/Courses/Info/<id>/<token>", methods=["GET","POST"])
@login_required
def course_info(id,token):

    role=3
    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    url_id=str(id)

    form=ModalApprovedForm()

    if  current_user.role_id == 1:

        with session_manager() as session:


            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            data=session.query(User,Curso).join(Curso, Curso.postulanteCurso_id==User.id).filter(Curso.id==url_id).first()
            course_objectives=session.query(CourseObjectives).filter(CourseObjectives.curso_id==url_id).all()
            course_BudgetItems=session.query(CourseBudgetsItems).filter(CourseBudgetsItems.curso_id==url_id).all()
            course_collaborators=session.query(CourseCollaborators).filter(CourseCollaborators.curso_id==url_id).all()
            #return(str(data)+"\n"+str(course_objectives)+"\n"+str(course_BudgetItems)+"\n"+str(course_collaborators))

            ### Preguntar ue es output?
            if data:

                d=data

                course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                hostName=d[1].hostName,hostAddress=d[1].hostAddress,coordName=d[1].coordName,coordTitle=d[1].coordTitle,\
                coordAffiliation=d[1].coordAffiliation,comDate=d[1].commDate,termDate=d[1].termDate,\
                description=d[1].courseDescription,organizationTraining=d[1].organizationTrainingDescription,\
                trainees=d[1].courseTrainees,output="Lorem ipsum, ipsum,ipsum",\
                objectives=course_objectives,budget=course_BudgetItems,\
                collaborators=course_collaborators,more=url_for('asign_evaluator_courses',id=url_id,token=user_id),evaluations=[])

                return render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course =course,user={"name":current_user.name,"token":current_user.token},\
                course_data={"id": url_id },form=form)

            else:
                return("No lograste entrar en data ")


    elif current_user.role_id== 2:

        with session_manager() as session:

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses

            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            data=session.query(User,Curso).join(Curso, Curso.postulanteCurso_id==User.id).filter(Curso.id==url_id).first()
            course_objectives=session.query(CourseObjectives).filter(CourseObjectives.curso_id==url_id).all()
            course_BudgetItems=session.query(CourseBudgetsItems).filter(CourseBudgetsItems.curso_id==url_id).all()
            course_collaborators=session.query(CourseCollaborators).filter(CourseCollaborators.curso_id==url_id).all()
            evaluations=session.query(EvaluationCourses).filter_by(curso_id=url_id,evaluator_id=current_user.id).all()

            if data:

                d=data
                course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                hostName=d[1].hostName,hostAddress=d[1].hostAddress,coordName=d[1].coordName,coordTitle=d[1].coordTitle,\
                coordAffiliation=d[1].coordAffiliation,comDate=d[1].commDate,termDate=d[1].termDate,\
                description=d[1].courseDescription,organizationTraining=d[1].organizationTrainingDescription,\
                trainees=d[1].courseTrainees,output="Lorem ipsum, ipsum,ipsum",\
                objectives=course_objectives,budget=course_BudgetItems,\
                collaborators=course_collaborators,more=url_for('asign_evaluator_courses',id=url_id,token=token),evaluations=evaluations)

                return render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course =course,\
                pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow},\
                user={"name":current_user.name,"token":current_user.token},course_data={"id":url_id},form=form)

            else:
                return("No lograste entrar en data ")

    else:

        with session_manager() as session:

            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            # data=session.query(User).get(user_id)
            # #curso=session.query(Curso).filter(Curso.postulanteCurso_id==user_id,Curso.id==url_id).all()
            # curso=session.query(Curso).filter(Curso.postulanteCurso_id==url_id).all()
            data=session.query(User,Curso).join(Curso, Curso.postulanteCurso_id==User.id).filter(Curso.id==url_id).first()
            course_objectives=session.query(CourseObjectives).filter(CourseObjectives.curso_id==url_id).all()
            course_BudgetItems=session.query(CourseBudgetsItems).filter(CourseBudgetsItems.curso_id==url_id).all()
            course_collaborators=session.query(CourseCollaborators).filter(CourseCollaborators.curso_id==url_id).all()
            evaluations=session.query(EvaluationCourses).filter_by(curso_id=url_id).all()

            ##aqui debo arreglar la data del querie para hacer la validacion de las evaluaciones
            if data:

                d=data
                course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                hostName=d[1].hostName,hostAddress=d[1].hostAddress,coordName=d[1].coordName,coordTitle=d[1].coordTitle,\
                coordAffiliation=d[1].coordAffiliation,comDate=d[1].commDate,termDate=d[1].termDate,\
                description=d[1].courseDescription,organizationTraining=d[1].organizationTrainingDescription,\
                trainees=d[1].courseTrainees,output="Lorem ipsum, ipsum,ipsum",\
                objectives=course_objectives,budget=course_BudgetItems,\
                collaborators=course_collaborators,more=url_for('asign_evaluator_courses',id=url_id,token=d[1].user_candidateId),\
                evaluations=evaluations)

                return render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course =course,user={"name":current_user.name,"token":current_user.token},\
                course_data={"id":url_id},form=form )

            else:
                return("No lograste entrar en data ")

            return render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course=course,user={"name":current_user.name,"token":current_user.token},\
            course_data={"id":url_id},form=form) #current_user.role_id,  course =course)


# @admin_permission.require()
@application.route("/dashboard")
@login_required
def dashboard():

    with session_manager() as session:

        users=session.query(User).count()
        courses=session.query(Curso).count()
        fellows=session.query(Fellow).count()
        total_evaluations=10

        db_state={"users":users,
        "courses":courses,
        "fellows":fellows,
        "total_e":total_evaluations}

    return render_template('dashboard.html',avatar_url=current_user.profile_picture,user_level = 3, data=db_state)


@application.route("/Users")
@login_required
def user():

    users=[]
    with session_manager() as session:
        u1=session.query(User).all()
        for u in u1:
            usuario=dict(name=u.name,lastName=u.lastname,role=ROLES[str(u.role_id)],\
            mail= u.email,lastSeen="dummy",more="/Profile",token=u.token)
            users.append(usuario)
            print(users)

    return render_template('users.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, users_list = users)


@application.route("/Asignments/Courses")
@login_required
def asign_courses():

    with session_manager() as session:

        pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending=pending_fellow+pending_courses

        asign_courses=[]
        #asign=session.query(Fellow).join('users').filter_by(id=current_user.id).all()

        ##Query many-to-many
        #data=session.query(Fellow).join('users').filter_by(id=current_user.id).all()
        completed=session.query(evaluandocourses_table).filter_by(evaluation_status=False,user_id=current_user.id).all()
        keys=[ c.curso_id for c in completed]

        ## Hago un query de todos los cursos que no he evaluado
        data=session.query(Curso).filter(Curso.id.in_(keys)).all()

        ## Query para obtener los datos del que postulo el curso

        #user=session.query(User).get(data)
        #return(str(asign))

        if data:
            for d in data:
                asign_curso= dict(name=d.user_candidateName,lastName=d.user_candidateLastName,title=d.courseTitle,\
                institution=d.hostAddress,citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.hostName,description=d.courseDescription,\
                date=d.commDate,more="Evaluate/Course/"+str(d.id))
                # asign_fellow = dict(name="Daniel" + i, lastName= "Ceviche " + i , title = "fellow" + i, institution= i + " college",
                # more = "/Evaluate/Fellow", citizenship="Venezuelan", status="in Progress", destination="Japon", description="Esto es un fellow", date="12/12/" +i)
                asign_courses.append(asign_curso)

            return render_template('asign_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,asign_courses_list=asign_courses,\
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

        else:
            return render_template('asign_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,asign_courses_list=asign_courses,pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

    #return render_template('asign_courses.html',user_level = rol, asign_courses_list = asign_courses)

@application.route("/Asignments/Fellow")
@login_required
def asign_fellow():

    with session_manager() as session:


        pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending=pending_fellow+pending_courses

        asign_fellows=[]
        #asign=session.query(Fellow).join('users').filter_by(id=current_user.id).all()

        ##Query many-to-many
        #data=session.query(Fellow).join('users').filter_by(id=current_user.id).all()
        completed=session.query(evaluandofellows_table).filter_by(evaluation_status=False,user_id=current_user.id).all()
        keys=[ c.fellow_id for c in completed]

        ## Hago un query de todos los fellows que he evalado
        data=session.query(Fellow).filter(Fellow.id.in_(keys)).all()

        #user=session.query(User).get(data)
        #return(str(asign))

        if data:
            for d in data:
                asign_fellow= dict(name=d.name,lastName=d.lastName,title=d.fellowTitle,\
                institution="Verificar bien cual es este dato",citizenship=d.citizenship,status=d.status_aprobado,\
                destination=d.destination,description="Descripcion no existe en el modelos actual",\
                data=d.creation_date,more="Evaluate/Fellow/"+d.fellow_userTokenId)
                # asign_fellow = dict(name="Daniel" + i, lastName= "Ceviche " + i , title = "fellow" + i, institution= i + " college",
                # more = "/Evaluate/Fellow", citizenship="Venezuelan", status="in Progress", destination="Japon", description="Esto es un fellow", date="12/12/" +i)
                asign_fellows.append(asign_fellow)

            return render_template('asign_fellow.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,asign_fellow_list=asign_fellows,\
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})


        else:
            return render_template('asign_fellow.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,asign_fellow_list=asign_fellows,\
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})


    #return render_template('asign_fellow.html',user_level = rol, asign_fellow_list = asign_fellows)

@application.route("/Evaluations/Courses")
@login_required
def eval_courses():

    with session_manager() as session:

        pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending=pending_fellow+pending_courses

        eval_courses=[]
        #asign=session.query(Fellow).join('users').filter_by(id=current_user.id).all()

        ##Query many-to-many
        #data=session.query(Fellow).join('users').filter_by(id=current_user.id).all()
        completed=session.query(evaluandocourses_table).filter_by(evaluation_status=True,user_id=current_user.id).all()
        keys=[ c.curso_id for c in completed]

        ## Hago un query de todos los cursos que no he evaluado
        data=session.query(Curso).filter(Curso.id.in_(keys)).all()

        score=session.query(EvaluationCourses.overallQualification).filter(EvaluationCourses.curso_id.in_(keys),\
        EvaluationCourses.evaluator_id==current_user.id)

        #user=session.query(User).get(data)
        #return(str(asign))

        if data:

            for d,s in zip(data,score):
                ### solucion muy temporal mientras borro la db
                ### Necesito colocar quien postulo el curso

                eval_course= dict(name=d.user_candidateName,lastName=d.user_candidateLastName,title=d.courseTitle,\
                institution=d.hostAddress,citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.hostName,description=d.courseDescription,\
                date=d.commDate,score=s[0],more=url_for('course_info',id=d.id,token=d.user_candidateId) )
                # asign_fellow = dict(name="Daniel" + i, lastName= "Ceviche " + i , title = "fellow" + i, institution= i + " college",
                # more = "/Evaluate/Fellow", citizenship="Venezuelan", status="in Progress", destination="Japon", description="Esto es un fellow", date="12/12/" +i)
                eval_courses.append(eval_course)

            return render_template('eval_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,eval_courses_list=eval_courses,
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

        else:
            return render_template('eval_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,eval_courses_list=eval_courses,
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})


@application.route("/Evaluations/Fellow")
@login_required
def evaluated_fellow_test():

    eval_fellows=[]

    with session_manager() as session:


        pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
        pending=pending_fellow+pending_courses



        completed=session.query(evaluandofellows_table).filter_by(evaluation_status=True,user_id=current_user.id).all()
        keys=[ c.fellow_id for c in completed]

        ## Hago un query de todos los fellows que he evaluado
        data=session.query(Fellow).filter(Fellow.id.in_(keys)).all()

        ## Arreglo la informacion para mandarla al front-end
        if data:
            for d in data:
                eval_fellow= dict(name=d.name,lastName="Dato_cambiar",title=d.fellowTitle,\
                institution="Verificar bien cual es este dato",citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.destination,description="Descripcion no existe en el modelos actual",\
                data=d.creation_date,more=url_for('fellow_info',token=d.fellow_userTokenId) )
                eval_fellows.append(eval_fellow)


            return render_template('eval_fellow.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,eval_fellows_list=eval_fellows,
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

        else:
            return render_template('eval_fellow.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,eval_fellows_list=eval_fellows,
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

    #return render_template('eval_fellow.html',user_level = rol, eval_fellows_list = eval_fellows)

# @app.route("/Users")
# def users_test():
#     return render_template('users.html',user_level = rol, users_list = users)


@application.route("/user_profile")
def user_profile():


    if request.method=="GET":

        with session_manager() as session:

            u=session.query(User).get(current_user.id)

            form=EditProfileForm(obj=u)

            return render_template("user_profile.html",avatar_url=current_user.profile_picture,user=u,form=form)



@application.route("/Profile/<token>")
@login_required
def profile(token):

    form = ModalRoleForm()

    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:

        return("Ocurrio un error" + str(e) )

    with session_manager() as session:
        u=session.query(User).get(user_id)
        Profile = dict(name=u.name, lastName=u.lastname , dateBirth =u.birth_date, mail=u.email, citizenship=u.citizenship,
        maritalStatus =u.marital_status, gender=u.gender, role=ROLES[str(u.role_id)], country=u.country, state="Miranda", city=u.city, address=u.address,
        phoneNumber =u.phonenumber, mobileNumber=u.cellphone, institution=u.institution, faculty=u.faculty, section=u.section, academicLevel=u.max_academic_level,
        studyLevel=u.current_academic_level, workplace=u.work_place ,zip=u.zip_code,token=u.token)

    return render_template('profile.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, user = Profile, form=form)

@application.route("/Profile/Fellows/<token>")
@login_required
def profile_fellow(token):

    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:

        return("Ocurrio un error" + str(e) )

    fellows=[]
    u=[]
    with session_manager() as session:

        data=session.query(User,Fellow).join(Fellow,User.id==Fellow.id).filter(Fellow.id==user_id)
        data2=session.query(User).get(user_id)
        u={"name":data2.name,"lastName":data2.lastname}

        if data:

            for d in data:
                fellow=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].fellowTitle,\
                institution=d[0].institution,citizenship=d[0].citizenship,evaluations=d[1].revisiones_completadas,
                status=d[1].status_aprobado,place=d[1].destination,\
                token=d[0].token)
                fellows.append(fellow)


        else:
            ## ponerle despues el current user a todo
            return render_template("error_form.html", error="No se consiguio ningun usuario valido")

    return render_template('profile_fellow.html',user_level = 3, fellows_list = fellows, user=u)

@application.route("/Profile/Courses/<token>")
@login_required
def profile_courses(token):

    courses = []

    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:

        return("Ocurrio un error" + str(e) )

    with session_manager() as session:

            #data=session.query(Curso).join(Curso).filter(Curso.postulanteCurso_id==user_id).all()
            data=session.query(Curso).filter(Curso.postulanteCurso_id==user_id).all()

            data2=session.query(User).get(user_id)
            u={"name":data2.name,"lastName":data2.lastname,"id":data2.token}

            if data:

                for d in data:

                    course=dict(title=d.courseTitle,\
                    institution=d.hostAddress ,evaluations=d.revisiones_completadas,\
                    requested=d.status_revisado,approved= d.status_aprobado ,status=d.status_aprobado,place=d.hostAddress,\
                    id=d.id)
                    courses.append(course)

            else:

                return render_template("error_form.html", error="No se consiguio ningun curso valido")
    # Arreglar este template pero primero debo arreglar la base de datos
    return render_template('profile_courses.html',user_level =3 , courses_list = courses, user=u)

@application.route("/ChangeRole/<token>",methods=["POST","GET"])
@login_required
def change_role(token):

    user=3

    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" +str(e))

    form = ModalRoleForm()

    if request.method=="POST" and form.validate_on_submit:

        data=request.form['roles']
        role=parsing_data(data)

        if role=="Standard":

            with session_manager() as session:

                u1=session.query(User).get(user_id)
                if u1.role_id==1:

                    return("User already have that role")

                else:

                    role=session.query(Role).get(1)
                    role.users.append(u1)
                    return("Role has changed")

        elif role=="Assistant":

            ## if current_user.role_id=3
            if user==3:
                with session_manager() as session:

                    u2=session.query(User).get(user_id)

                    if u2.role_id==4:

                        return("User already have that role")

                    else:

                        role=session.query(Role).get(4)
                        role.users.append(u2)
                        return("Role has changed")

        else:

            with session_manager() as session:

                user_invitado=session.query(User).get(user_id)

                if user_invitado.role_id==2:

                    return ("EL usuario ya tiene un rol asignado")

                else:

                    user_invitado.possible_evaluator=1
                    noti=Notifications("Invitacion a Evaluar","Haz sido invitado a evaluar postulaciones en la plataforma de BIOLAC",\
                    datetime.datetime.now(),"permiso_evaluacion")
                    user_invitado.notifications.append(noti)

                    session.add(noti)
                    session.add(user_invitado)

                    try:
                        token = ts.dumps(user_invitado.email, salt='email-confirmation')

                    except Exception as e:
                        ## Algun error para la funcion e imprime el error
                        return("Ocurrio un error:" + str(e))

                    ## Genero el url con el token necesario (RED LOCAL)

                    #confirm_url = url_for( 'validation', token=token,_external=True)
                    confirm_url=IP_DOMAIN+"/aceptar/"+str(token)

                    ## Hago una plantilla con jinja que la cual tendra el contenido del correo
                    html=render_template('_solicitud_evaluacion.html',confirm_url=confirm_url)

                    ## Anexando la informacion al correo especificado
                    send_email(SUBJECT_INVITATION,application.config["MAIL_USERNAME"],[user_invitado.email],html)
                    # msg = Message(SUBJECT_INVITATION, sender=application.config["MAIL_USERNAME"], recipients=[DUMMY_MAIL])
                    # msg.body = html
                    # mail.send(msg)

                    return("Probando si funciono")

    else:
        return("String prueba")


@application.route("/Error")
def error_test():
    return render_template('error_form.html')


# @app.route('/invitar')
# def invitar():
#
#
#
#     with session_manager() as session:
#         user_invitado=session.query(User).filter_by(correo='cristhian8bravo@gmail.com').one()
#         user_invitado.possible_evaluator=True
#
#
#         try:
#             token = ts.dumps(user.email, salt='email-confirmation')
#
#         except Exception as e:
#             ## Algun error para la funcion e imprime el error
#             return("Ocurrio un error:" + str(e))
#
#         ## Genero el url con el token necesario (RED LOCAL)
#
#         #confirm_url = url_for( 'validation', token=token,_external=True)
#         confirm_url=IP+"/aceptar/"+str(token)
#
#         ## Hago una plantilla con jinja que la cual tendra el contenido del correo
#         html=render_template('_solicitud_evaluacion.html',confirm_url=confirm_url)
#
#         ## Anexando la informacion al correo especificado
#         msg = Message(SUBJECT_INVITATION, sender=app.config["MAIL_USERNAME"], recipients=[DUMMY_MAIL])
#         msg.body = html
#         mail.send(msg)

@application.route("/aceptar/<token>")
def aceptar(token):

    try:
        email = ts.loads(token, salt="email-confirmation", max_age=18000)
    except Exception as e:
        print(e)
        return(str(e))


    with session_manager() as session:

        u=session.query(User).filter_by(email=email).first()
        u.possible_evaluator=False

        notif=Notifications("Usuario acepto la invitacion a evaluar","Usuario: "+str(u.name)+ " " + str(u.email)+" acepto la invitacion de ser evaluador",\
        datetime.datetime.now(),"permiso_evaluar_aceptado")

        role=session.query(Role).get(2)
        role.users.append(u)

        administrador=session.query(User).get(2)
        administrador.notifications.append(notif)

        session.add(notif)
        session.add(administrador)


    return render_template("evaluator_assigned.html")
    #return redirect(url_for('login'))


@application.route("/Asignments/Evaluate/Course/<id>",methods=["GET","POST"])
@login_required
def evaluate_form_course(id):

    """ Aqui tomo el user_id token y busco los datos para pre rellenar el
    formulario Fellow.id==user_id"""


    url_id=int(id)

    # try:
    #     user_id_link = serializer.loads(token, salt="passing_id")
    #     user_id_link=int(user_id_link)
    #
    # except Exception as e:
    #
    #     return("Ocurrio un error linea 1429" + str(e) )

    if request.method=="GET":

        with session_manager() as session:

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses


            ## el query es contra el cursoid que  recibo en el url
            d=session.query(Curso).filter(Curso.id==url_id).first()
            course_objectives=session.query(CourseObjectives).filter(CourseObjectives.curso_id==url_id).all()
            course_BudgetsItems=session.query(CourseBudgetsItems).filter(CourseBudgetsItems.curso_id==url_id).all()
            course_collaborators=session.query(CourseCollaborators).filter(CourseCollaborators.curso_id==url_id).all()


            if d:

                course=dict(name= d.courseTitle,lastName=d.courseTitle,title=d.courseTitle,\
                hostName=d.hostName,hostAddress=d.hostAddress,coordName=d.coordName,coordTitle=d.coordTitle,\
                coordAffiliation=d.coordAffiliation,comDate=d.commDate,termDate=d.termDate,\
                description=d.courseDescription,organizationTraining=d.organizationTrainingDescription,\
                trainees=d.courseTrainees,output="Lorem ipsum, ipsum,ipsum",\
                objectives=course_objectives,budget=course_BudgetsItems,\
                collaborators=course_collaborators,id=url_id,\
                evaluations=[])
                print(str(course))

            else:

                return("No lograste entrar en data ")

            ## Prepopulo los campos en el form
            course_data=session.query(EvaluationCoursesBackup).filter(EvaluationCoursesBackup.evaluator_id==current_user.id,EvaluationCoursesBackup.curso_id==url_id).first()

            print(course_data)

            ## Si hay data de cursos salvada
            if course_data:

                print(course_data)
                ## Rellena el formulario con esa data
                form=MiniForm(obj=course_data)

            else:
                ## Si no devuelve el formulario sin mas problema
                form=MiniForm()

            return render_template('eval_form_course.html',avatar_url=current_user.profile_picture, user_level=current_user.role, course = course, form = form,\
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow},\
            user={"token":current_user.token,"name":current_user.name})

    elif request.method=="POST":

        form= MiniForm()

        if form.validate_on_submit:

            objectiveComment = request.form['objectiveComment']
            descriptionComment= request.form['descriptionComment']
            collaboratorsComment= request.form['collaboratorsComment']
            budgetComment = request.form['budgetComment']
            traineesComment =request.form['traineesComment']
            finalComment = request.form['finalComment']
            overallQualification = request.form['overallQualification']

            with session_manager() as session:

                c1=session.query(Curso).filter_by(id=url_id).first()
                u1=session.query(User).filter_by(id=current_user.id).first()

                try:
                    evaluation=EvaluationCourses(objectiveComment,descriptionComment,\
                    collaboratorsComment,budgetComment,traineesComment,\
                    finalComment,overallQualification,\
                    evaluator_id=current_user.id,evaluator_name=current_user.name,\
                    evaluator_email=current_user.email,evaluator_lastName=current_user.lastname)

                    ## Lleno el log con la información necesaria
                    ## arreglar esto cuando cree un curso debo agregarle el correo del postulante
                    log=LogEvaluadores(current_user.name,current_user.email,"Course",c1.id,c1.courseTitle,current_user.email)

                    ## Agrego la evaluacion al log
                    u1.completed_users_evaluations.append(log)

                    ## Agrego la evaluacion al fellow para tener la relacion de la llave foranea
                    c1.course_evaluations.append(evaluation)

                    ## Aumento la cantidad de evaluados
                    c1.revisiones_completadas=c1.revisiones_completadas+1

                    ## Cambio el estado de la evaluacion en la joining table
                    result= session.execute('UPDATE evaluandocourses SET evaluation_status = True WHERE user_id= :val1 AND curso_id= :val2' , {'val1':current_user.id,'val2':url_id})
                    # status=session.query(evaluandofellows_table).filter_by(fellow_id=user_id_link,user_id=current_user.id).first()#.update({evaluandofellows_table.evaluation_status:True})
                    # status.evaluation_status=True
                    ## Agregamos todos los objetos a la session

                    noti=Notifications("Evaluacion Curso","El usuario "+str(current_user.name)+\
                    " " + str(current_user.email)+" Evaluo un curso",\
                    datetime.datetime.now(),"evaluacion_curso")

                    administrador=session.query(User).get(2)
                    administrador.notifications.append(noti)

                    session.add(evaluation)
                    session.add(c1)
                    session.add(u1)
                    session.add(noti)

                except Exception as e:
                    return("Ocurrio un error linea 1487: " + str(e))


            return redirect(url_for('asign_courses'))

    # # try:
    # #     user_id = serializer.loads(token, salt="passing_id")
    # #     user_id=int(user_id)
    # #
    # # except Exception as e:
    # #
    # #     return("Ocurrio un error" + str(e) )
    #
    # with session_manager() as session:
    #
    #     data=session.query(Fellow,FellowObjectives,FellowActivities)\
    #     .join(FellowObjectives)\
    #     .join(FellowActivities)\
    #     .filter(Fellow.id==6).all() ## aqui usaremos current_user.id
    #     return(str(data))
    #
    #
    # form = MiniForm()

    #return render_template('eval_form_course.html', user_level=rol, course = course, form = form)

@application.route("/Asignments/Evaluate/Fellow/<token>",methods=["GET","POST"])
@login_required
def evaluate_form_fellow(token):

    try:
        user_id_link = serializer.loads(token, salt="passing_id")
        user_id_link=int(user_id_link)

    except Exception as e:

        return("Ocurrio un error linea 1429" + str(e) )

    if request.method=="GET":

        with session_manager() as session:

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses

            ## el query es contra el user id que  recibo en el url
            d=session.query(Fellow).filter(Fellow.id==user_id_link).first()
            fellow_objectives=session.query(FellowObjectives).filter(FellowObjectives.fellow_id==user_id_link).all()
            fellow_activities=session.query(FellowActivities).filter(FellowActivities.fellow_id==user_id_link).all()

            # print(str(fellow_objectives))
            # return(str(d))
            if d:

                fellow=dict(name= d.name,lastName="Esto parece ser innecesario",title=d.fellowTitle,\
                institution="Revisar que host institution",generalObjective=d.generalObjective,justification=d.methodology,plan=d.workingPlan,\
                citizenship="Este campo no es necesario",evaluations=d.revisiones_completadas,
                status=d.status_aprobado,destination="Revisar que es este campo",\
                token=d.fellow_userTokenId,objectives=fellow_objectives,activities=fellow_activities)

            else:

                return("No se consiguio ninguna data ")


            fellow_data_saved=session.query(EvaluationFellowsBackup).filter(EvaluationFellowsBackup.evaluator_id==current_user.id,\
            EvaluationFellowsBackup.fellow_id==user_id_link).first()

            print(fellow_data_saved)

            ## Si hay data de cursos salvada
            if fellow_data_saved:

                ## Rellena el formulario con esa data
                form=MiniForm2(obj=fellow_data_saved)

            else:
                ## Si no devuelve el formulario sin mas problema

                form=MiniForm2()
                form.process()

            return render_template('eval_form_fellow.html',avatar_url=current_user.profile_picture, user_level=current_user.role, fellow = fellow, form = form,\
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow},\
            user={"token":current_user.token,"name":current_user.name})


    elif request.method=="POST":

        form= MiniForm2()

        if form.validate_on_submit:

            previousInvestigationScore = request.form['previousInvestigationScore']
            previousInvestigation = request.form['previousInvestigation']
            currentInvestigationScore = request.form['currentInvestigationScore']
            currentInvestigation = request.form['currentInvestigation']
            purposeApplicationScore  = request.form['purposeApplicationScore']
            purposeApplication =request.form['purposeApplication']
            finalReviewScore = request.form['finalReviewScore']
            finalReview = request.form['finalReview']
            otherTrainingCoursesScore = request.form['otherTrainingCoursesScore']
            otherTrainingCourses =  request.form['otherTrainingCourses']

            with session_manager() as session:

                f1=session.query(Fellow).filter_by(id=user_id_link).first()
                u1=session.query(User).filter_by(id=current_user.id).first()

                try:
                    evaluation=EvaluationFellows(previousInvestigationScore,previousInvestigation,\
                    currentInvestigationScore,currentInvestigation,purposeApplicationScore,\
                    purposeApplication,otherTrainingCoursesScore,otherTrainingCourses,\
                    finalReviewScore,finalReview,evaluator_id=current_user.id,evaluator_name=current_user.name)

                    ## Lleno el log con la información necesaria
                    log=LogEvaluadores(current_user.name,current_user.email,"Fellow",f1.id,f1.fellowTitle,f1.fellow_candidateEmail)

                    ## Agrego la evaluacion al log
                    u1.completed_users_evaluations.append(log)

                    ## Agrego la evaluacion al fellow para tener la relacion de la llave foranea
                    f1.fellow_evaluations.append(evaluation)

                    ## Aumento la cantidad de evaluados
                    f1.revisiones_completadas=f1.revisiones_completadas+1

                    ## Cambio el estado de la evaluacion en la joining table
                    result= session.execute('UPDATE evaluandofellows SET evaluation_status = True WHERE user_id= :val1 AND fellow_id= :val2' , {'val1':current_user.id,'val2':user_id_link})
                    # status=session.query(evaluandofellows_table).filter_by(fellow_id=user_id_link,user_id=current_user.id).first()#.update({evaluandofellows_table.evaluation_status:True})
                    # status.evaluation_status=True

                    noti=Notifications("Evaluacion Fellow","El usuario "+str(current_user.name)+\
                    " " + str(current_user.email)+" Evaluo un fellow",\
                    datetime.datetime.now(),"evaluacion_fellow")

                    administrador=session.query(User).get(2)
                    administrador.notifications.append(noti)


                    ## Agregamos todos los objetos a la session
                    session.add(evaluation)
                    session.add(f1)
                    session.add(u1)
                    session.add(noti)

                    backup_data=session.query(EvaluationFellowsBackup).filter_by(fellow_id=user_id_link).first()

                    if backup_data:

                        session.delete(backup_data)


                except Exception as e:
                    return("Ocurrio un error linea 1487: " + str(e))

                # try:
                #     fellow=session.query(Fellow).filter(Fellow.id==user_id).update({Fellow.revisiones_completadas:Fellow.revisiones_completadas+1})
                # except Exception as e:
                #     session.rollback()
                #     return("Ocurrio un error: " + str(e))

            return redirect(url_for('asign_fellow'))


@application.route("/Evaluators/Fellows/List/<token>" , methods=["GET","POST"])
@login_required
def total_user_Evaluated(token):

    try:
        u_id = serializer.loads(token, salt="passing_id")
        u_id=int(u_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    eval_fellows=[]

    with session_manager() as session:

        completed=session.query(evaluandofellows_table).filter_by(evaluation_status=True,user_id=u_id).all()
        keys=[ c.fellow_id for c in completed]

        print(keys)
        ## Hago un query de todos los fellows que he evaluado
        data=session.query(Fellow).filter(Fellow.id.in_(keys)).all()

        print(str(data))
        ## Arreglo la informacion para mandarla al front-end
        if data:
            for d in data:
                eval_fellow= dict(name=d.name,lastName="Dato_cambiar",title=d.fellowTitle,\
                institution="Verificar bien cual es este dato",citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.destination,description="Descripcion no existe en el modelos actual",\
                data=d.creation_date,more=url_for('fellow_info',token=d.fellow_userTokenId) )
                eval_fellows.append(eval_fellow)
        else:
            return("No consegui nada en la data de envio")


        return render_template("profile_eval_fellow.html",avatar_url=current_user.profile_picture,user_level=current_user.role_id,user={"token":current_user.token,"name":current_user.name},\
        eval_fellows_list=eval_fellows)

@application.route("/Evaluators/Courses/List/<token>" , methods=["GET","POST"])
@login_required
def total_courses_Evaluated(token):

    try:
        u_id = serializer.loads(token, salt="passing_id")
        u_id=int(u_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))


    with session_manager() as session:

        eval_courses=[]
        #asign=session.query(Fellow).join('users').filter_by(id=current_user.id).all()

        ##Query many-to-many
        #data=session.query(Fellow).join('users').filter_by(id=current_user.id).all()
        completed=session.query(evaluandocourses_table).filter_by(evaluation_status=True,user_id=u_id).all()
        keys=[ c.curso_id for c in completed]

        ## Hago un query de todos los cursos que no he evaluado
        data=session.query(Curso).filter(Curso.id.in_(keys)).all()

        #user=session.query(User).get(data)
        #return(str(asign))

        if data:

            for d in data:
                ### solucion muy temporal mientras borro la db
                ### Necesito colocar quien postulo el curso

                eval_course= dict(name="Cambiar por lo que sea ",lastName="Dato_cambiar",title=d.courseTitle,\
                institution=d.hostAddress,citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.hostName,description="Descripcion no existe en el modelos actual",\
                date=d.commDate,more=url_for('course_info',id=d.id,token=d.user_candidateId) )
                # asign_fellow = dict(name="Daniel" + i, lastName= "Ceviche " + i , title = "fellow" + i, institution= i + " college",
                # more = "/Evaluate/Fellow", citizenship="Venezuelan", status="in Progress", destination="Japon", description="Esto es un fellow", date="12/12/" +i)
                eval_courses.append(eval_course)

            return render_template('eval_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,eval_courses_list=eval_courses,\
            user={"token":current_user.token,"name":current_user.name})

        else:
            return render_template('eval_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,eval_courses_list=eval_courses,
            pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})


@application.route("/Asignments/Fellow/List/<token>")
@login_required
def asigned_to_evaluator_fellow(token):

    try:
        u_id = serializer.loads(token, salt="passing_id")
        u_id=int(u_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    with session_manager() as session:

        asign_fellows=[]
        #asign=session.query(Fellow).join('users').filter_by(id=current_user.id).all()

        ##Query many-to-many
        #data=session.query(Fellow).join('users').filter_by(id=current_user.id).all()
        completed=session.query(evaluandofellows_table).filter_by(evaluation_status=False,user_id=u_id).all()
        keys=[ c.fellow_id for c in completed]

        ## Hago un query de todos los fellows que he evalado
        data=session.query(Fellow).filter(Fellow.id.in_(keys)).all()

        #user=session.query(User).get(data)
        #return(str(asign))

        if data:
            for d in data:
                asign_fellow= dict(name=d.name,lastName="Dato_cambiar",title=d.fellowTitle,\
                institution="Verificar bien cual es este dato",citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.destination,description="Descripcion no existe en el modelos actual",\
                data=d.creation_date,more="Evaluate/Fellow/"+d.fellow_userTokenId)
                # asign_fellow = dict(name="Daniel" + i, lastName= "Ceviche " + i , title = "fellow" + i, institution= i + " college",
                # more = "/Evaluate/Fellow", citizenship="Venezuelan", status="in Progress", destination="Japon", description="Esto es un fellow", date="12/12/" +i)
                asign_fellows.append(asign_fellow)

            return render_template('profile_asign_fellows.html',avatar_url=current_user.profile_picture,\
            user_level=current_user.role_id,asign_fellow_list=asign_fellows,\
            user={"token":current_user.token,"name":current_user.name})


        else:
            return render_template('profile_asign_fellows.html',avatar_url=current_user.profile_picture,\
            user_level=current_user.role_id,asign_fellow_list=asign_fellows,\
            user={"token":current_user.token,"name":current_user.name})


    #return render_template('asign_fellow.html',user_level = rol, asign_fellow_list = asign_fellows)



@application.route("/Asignments/Courses/List/<token>")
@login_required
def asigned_to_evaluator(token):

    try:
        u_id = serializer.loads(token, salt="passing_id")
        u_id=int(u_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    with session_manager() as session:


        asign_courses=[]
        #asign=session.query(Fellow).join('users').filter_by(id=current_user.id).all()

        ##Query many-to-many
        #data=session.query(Fellow).join('users').filter_by(id=current_user.id).all()
        completed=session.query(evaluandocourses_table).filter_by(evaluation_status=False,user_id=u_id).all()
        keys=[ c.curso_id for c in completed]

        ## Hago un query de todos los cursos que no he evaluado
        data=session.query(Curso).filter(Curso.id.in_(keys)).all()

        #user=session.query(User).get(data)
        #return(str(asign))

        if data:
            for d in data:
                asign_curso= dict(name="Cambiar por lo que sea ",lastName="Dato_cambiar",title=d.courseTitle,\
                institution=d.hostAddress,citizenship="Dato_cambiar",status=d.status_aprobado,\
                destination=d.hostName,description="Descripcion no existe en el modelos actual",\
                date=d.commDate,more=url_for('course_info',id=d.id,token=token))
                # asign_fellow = dict(name="Daniel" + i, lastName= "Ceviche " + i , title = "fellow" + i, institution= i + " college",
                # more = "/Evaluate/Fellow", citizenship="Venezuelan", status="in Progress", destination="Japon", description="Esto es un fellow", date="12/12/" +i)
                asign_courses.append(asign_curso)

            return render_template('profile_asign_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,asign_courses_list=asign_courses,\
            user={"token":current_user.token,"name":current_user.name})

        else:
            return render_template('profile_asign_courses.html',avatar_url=current_user.profile_picture,user_level=current_user.role_id,asign_courses_list=asign_courses,pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})

@application.route("/savecourse/<token>",methods=["GET","POST"])
@login_required
def savecourse(token):

    try:
        u_id = serializer.loads(token, salt="passing_id")
        u_id=int(u_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    c1=CursoBackup()

    if len(c1.courseObjectives) == 0:
        c1.courseObjectives = [CourseObjectivesBackup()]

    if len(c1.courseBudgetItems) == 0:
        c1.courseBudgetItems = [CourseBudgetsItemsBackup()]

    if len(c1.courseCollaborators) == 0:
        c1.courseCollaborators = [CourseCollaboratorsBackup()]

    form=CourseForm(obj=c1)

    if request.method=="POST" and form.validate_on_submit():

        data=request.form
        print(data)

        file_dict={}
        i=1

        for archivo in request.files:

            path,realFilename,hashed_name=saving_files(request.files[archivo])
            file_dict['doc_curso'+str(i)]=[path,realFilename,hashed_name]
            i+=1



        for j in range(1,i):
            doc=DocumentosCursosBackup(file_dict["doc_curso"+str(j)][1],\
                file_dict["doc_curso"+str(j)][0],\
                file_dict["doc_curso"+str(j)][2])
            c1.cursoDocs.append(doc)
            c1.courseCollaborators.coll_cv=file_dict["doc_curso"+str(j)][0]

        form.populate_obj(c1)
        print(c1)
        with session_manager() as session:

            ### Agrego los campos criticos para el flujo de la aplicacion
            c1.user_candidateEmail=current_user.email
            c1.user_candidateId=current_user.token

            ## Agrego a el usuario postulante a el usuario
            u=session.query(User).get(current_user.id)
            u.curso.append(c1)
            session.add(c1)

            try:
                session.flush()
            except Exception as e:

                return("Ocurrion un error mientras hacia el flush", +str(e))

            log=LogApplications(c1.hostAddress,current_user.id,"Course",c1.courseTitle,current_user.email,current_user.id)
            session.add(log)

        return redirect(url_for('courses_application'))

    else:

        with session_manager() as session:

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            print(str(pending_fellow))
            pending=pending_fellow+pending_courses

        return render_template("course_form.html",avatar_url=current_user.profile_picture,user_level = current_user.role_id,form=form, user={"token":current_user.token,"name":current_user.name},\
        pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow})
    #return render_template('course_form.html',user_level = current_user.role_id,form=form)



# @application.route("/savefellow/<token>",methods=["GET","POST"])
# @login_required
# def savefellow(token):
#
#     try:
#         user_id = serializer.loads(token, salt="passing_id")
#         user_id=int(user_id)
#
#     except Exception as e:
#         return("Ocurrio un error:" + str(e))
#
#     form=FellowForm()
#
#     if request.method=="POST" and form.validate_on_submit:
#
#         print("Entre en el post")
#
#         with session_manager() as session:
#
#             saved_data=session.query(FellowBackup).filter(FellowBackup.id==current_user.id).first()
#
#             print(saved_data)
#
#             if saved_data:
#
#                 print(request.form)
#
#                 form.populate_obj(saved_data)
#
#                 session.add(saved_data)
#
#             else:
#
#                 print("Creando el que no existe")
#                 print("Este es el id que me mandaron:" +str(user_id))
#
#                 ## Creamos el objeto para el backup
#                 f1=FellowBackup()
#
#                 if len(f1.fellowObjectives) == 0:
#                     f1.fellowObjectives = [FellowObjectivesBackup()]
#
#                 if len(f1.fellowActivities) == 0:
#                     f1.fellowActivities = [FellowActivitiesBackup()]
#
#                 form= FellowForm(obj=f1)
#
#
#                 ## Agregando metadata util para los formularios
#                 f1.id=current_user.id
#                 f1.name=current_user.name
#                 f1.fellow_userTokenId=current_user.token
#                 f1.fellow_candidateEmail=current_user.email
#
#                 ## Rellenando el objeto con los datos del query
#                 form.populate_obj(f1)
#
#                 print("Imprimiendo data"+str(f1))
#
#                 ## Agregando todo a la session
#                 session.add(f1)
#
#         return("El backup fue realizado con exito")
#
#     else:
#
#         return("Probando Todo")


@application.route("/save_fellow_eval/<token>",methods=["GET","POST"])
@login_required
def save_fellow_eval(token):

    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    form=MiniForm2()

    if request.method=="POST":

        with session_manager() as session:

            saved_data=session.query(EvaluationFellowsBackup).filter(EvaluationFellowsBackup.evaluator_id==current_user.id,\
            EvaluationFellowsBackup.fellow_id==user_id).first()

            print(saved_data)

            if saved_data:

                print(request.form)

                previousInvestigationScore=request.form['previousInvestigationScore']
                previousInvestigation=request.form['previousInvestigation']
                currentInvestigationScore= request.form['currentInvestigationScore']
                currentInvestigation= request.form['currentInvestigation']
                purposeApplicationScore=request.form['purposeApplicationScore']
                purposeApplication=request.form['purposeApplication']
                otherTrainingCoursesScore=request.form['otherTrainingCoursesScore']
                otherTrainingCourses=request.form['otherTrainingCourses']
                finalReviewScore= request.form['finalReviewScore']
                finalReview= request.form['finalReview']


                saved_data.previousInvestigationScore=previousInvestigationScore
                saved_data.previousInvestigation=previousInvestigation
                saved_data.currentInvestigationScore=currentInvestigationScore
                saved_data.currentInvestigation=currentInvestigation
                saved_data.purposeApplicationScore=purposeApplicationScore
                saved_data.purposeApplication=purposeApplication
                saved_data.otherTrainingCoursesScore=otherTrainingCoursesScore
                saved_data.otherTrainingCourses=otherTrainingCourses
                saved_data.finalReviewScore=finalReviewScore
                saved_data.finalReview=finalReview

                session.add(saved_data)

            else:

                print("Creando el que no existe")
                print("Este es el id que me mandaron:" +str(user_id))
                ## Creamos el objeto para el backup
                f1=EvaluationFellowsBackup()

                ## Populamos con el contenido del request
                form.populate_obj(f1)

                ## Agregando alguna metadata util para e; proceso
                f1.evaluator_id=current_user.id
                f1.evaluator_name=current_user.name
                f1.evaluator_email=current_user.email

                print("Imprimiendo data"+str(f1))

                ## Agregando llave foranea al objeto
                fellow_data=session.query(Fellow).filter_by(id=user_id).first()
                fellow_data.fellow_evaluations_backup.append(f1)

                ## Agregando todo a la session
                session.add(f1)

        return("El backup fue realizado con exito")

    else:

        return("Probando Todo")

@application.route("/save_course_eval/<id>",methods=["GET","POST"])
@login_required
def save_course_eval(id):

    # try:
    #     user_id = serializer.loads(token, salt="passing_id")
    #     user_id=int(user_id)
    #
    # except Exception as e:
    #     return("Ocurrio un error:" + str(e))

    url_id=int(id)

    form=MiniForm()

    if request.method=="POST":

        with session_manager() as session:

            saved_data=session.query(EvaluationCoursesBackup).filter(EvaluationCoursesBackup.evaluator_id==current_user.id,\
            EvaluationCoursesBackup.curso_id==url_id).first()

            print(saved_data)

            if saved_data:

                ## Si ya hay data solo actualizo los valores
                print("Entre en el que existe")
                print(request.form)
                objectiveComment = request.form['objectiveComment']
                descriptionComment= request.form['descriptionComment']
                collaboratorsComment= request.form['collaboratorsComment']
                budgetComment = request.form['budgetComment']
                traineesComment =request.form['traineesComment']
                finalComment = request.form['finalComment']
                overallQualification = request.form['overallQualification']

                saved_data.objectiveComment=objectiveComment
                saved_data.descriptionComment=descriptionComment
                saved_data.collaboratorsComment=collaboratorsComment
                saved_data.budgetComment=budgetComment
                saved_data.traineesComment=traineesComment
                saved_data.finalComment=finalComment
                saved_data.overallQualification=overallQualification

                session.add(saved_data)

            else:

                print("Creando el que no existe")
                ## Creamos el objeto para el backup
                c1=EvaluationCoursesBackup()

                ## Populamos con el contenido del request
                form.populate_obj(c1)

                ## Agregando alguna metadata util para e; proceso
                c1.evaluator_id=current_user.id
                c1.evaluator_name=current_user.name

                print("Imprimiendo data"+str(c1))

                ## Agregando llave foranea al objeto
                course_data=session.query(Curso).filter_by(id=url_id).first()
                course_data.course_evaluations_backup.append(c1)

                ## Agregando todo a la session
                session.add(c1)

        return("El backup fue realizado con exito")

    else:

        return("Probando Todo")


@application.route("/prueba_multi",methods=["GET","POST"])
def multi():
    import datetime


    c1=Curso()

    if len(c1.courseObjectives) == 0:
        c1.courseObjectives = [CourseObjectives()]

    if len(c1.courseBudgetItems) == 0:
        c1.courseBudgetItems = [CourseBudgetsItems()]

    form=MiniCourse(obj=c1)

    if request.method=="POST" and form.validate_on_submit():

        data=request.form
        print(data)
        form.populate_obj(c1)
        for data in c1.courseObjectives:
            print(data)

        with session_manager() as session:

            session.add(c1)

        return("Todo Ok")
    else:

        return render_template("course_prueba.html",form=form)

@application.route("/delete/<token>",methods=["GET","POST"])
@login_required
def delete(token):

    try:
        u_id = serializer.loads(token, salt="passing_id")
        u_id=int(u_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    try:
        with session_manager() as session:
            user=session.query(User).get(u_id)
            fellow=session.query(Fellow).get(u_id)
            session.delete(user)
            session.delete(fellow)

    except Exception as e:
        return("No se logro borrar el usuario")

    return("Lograste borrar al usuario")



    return()

@application.route("/approve/<id>", methods=["GET","POST"])
@login_required
def approve(id):

    url_id=id

    form=ModalApprovedForm()

    if request.method == "POST" and form.validate_on_submit:

        budget=request.form["Approved_budget"]

        with session_manager() as session:

            c=session.query(Curso).filter(Curso.id==url_id).update({Curso.aprove_budget:budget,Curso.status_aprobado:"Aproved"})


        return("El budget fue asignado")
        # return(str(data))

@application.route("/deny/<id>", methods=["GET","POST"])
@login_required
def deny(id):

    url_id=int(id)

    if request.method == "POST":

        with session_manager() as session:

            c=session.query(Curso).filter(Curso.id==url_id).update({Curso.status_aprobado:"Denied"})

        return redirect("La aplicacion ya fue evaluada")

@application.route("/approve_fellow/<fellow_id>",methods=["POST"])
@login_required
def approve_fellow(fellow_id):

    fellow_id=int(fellow_id)

    if request.method == "POST":

        with session_manager() as session:

            f=session.query(Fellow).filter(Fellow.id==fellow_id).update({Fellow.status_aprobado:"Approved"})

        return redirect(url_for('fellow_application'))

@application.route("/deny_fellow/<fellow_id>",methods=["POST"])
@login_required
def deny_fellow(fellow_id):

    fellow_id=int(fellow_id)

    if request.method == "POST":

        with session_manager() as session:

            f=session.query(Fellow).filter(Fellow.id==fellow_id).update({Fellow.status_aprobado:"Denied"})

        return redirect(url_for('fellow_application'))


@application.route("/create")
def create():

    drop_db()
    init_db()

    with session_manager() as session:
        permiso1=Permisos("Ver cursos", "Permite a los usuarios ver los cursos disponibles")
        permiso2=Permisos("Ver historial","Permite observar el historial de las personas")
        permiso3=Permisos("Editar cursos","Permite editar las solicitudes de los cursos ")
        permiso4=Permisos("Editar becarios","Permite editar las solicitudes de los becarios")

        session.add(permiso1)
        session.add(permiso2)
        session.add(permiso3)
        session.add(permiso4)


    ## queries de la tabla de permisos para asignar
    with session_manager() as session:
        p1=session.query(Permisos).get(1)
        p2=session.query(Permisos).get(2)
        p3=session.query(Permisos).get(3)
        p4=session.query(Permisos).get(4)


        ## Definicion de los roles para los diferents usuarios

        role1=Role('estandar','usuarios normales entran con este rol')
        role1.permisos.append(p1)
        session.add(role1)

    with session_manager() as session:
        p1=session.query(Permisos).get(1)
        p2=session.query(Permisos).get(2)
        p3=session.query(Permisos).get(3)
        p4=session.query(Permisos).get(4)


        ## Definicion de los roles para los diferents usuarios

        role3=Role('evaluadores','Usuarios que pueden evaluar a los concursantes')
        role3.permisos.append(p1)
        role3.permisos.append(p4)
        session.add(role3)

    with session_manager() as session:
        p1=session.query(Permisos).get(1)
        p2=session.query(Permisos).get(2)
        p3=session.query(Permisos).get(3)
        p4=session.query(Permisos).get(4)


        ## Definicion de los roles para los diferents usuarios
        role0=Role('admin','Usuario con todos los permisos de la aplicacion')
        role0.permisos.append(p1)
        role0.permisos.append(p2)
        role0.permisos.append(p3)
        role0.permisos.append(p4)
        session.add(role0)

    with session_manager() as session:
        p1=session.query(Permisos).get(1)
        p2=session.query(Permisos).get(2)
        p3=session.query(Permisos).get(3)
        p4=session.query(Permisos).get(4)


        ## Definicion de los roles para los diferents usuarios
        role2=Role('asistentes','Usuario con menos permisos que los admin')
        role2.permisos.append(p1)
        role2.permisos.append(p2)
        role2.permisos.append(p3)
        session.add(role2)


    ## Creacion del primer usuario con su role
    with session_manager() as session:
        role_q=session.query(Role).get(1)
        token_id=serializer.dumps(str(1),salt="passing_id")
        user=User("cristhian3bravo@gmail.com","Hola12#","Cristhian","Bravo",datetime.datetime.now(),"Venezolano","Hombre",\
        "single","venezuela","Caracas",1061,"El cafetal","USB",\
        "algo","algo","bachiller","bachiller","usb",\
        "0412-7256957","0212-9858996",profile_picture="/images/default.jpg",token=token_id,mentor="Lobito",mentor_mail="lobito@reando.com")
        role_q.users.append(user)
        session.add(user)


    with session_manager() as session:
        role_q3=session.query(Role).get(3)
        token_id2=serializer.dumps(str(2),salt="passing_id")
        user3=User("cristhian6bravo@gmail.com","Hola12#","Cristhian","Perez",datetime.datetime.now(),"Venezolano","Hombre",\
        "single","venezuela","Caracas",1061,"El cafetal","USB",\
        "algo","algo","bachiller","bachiller","usb",\
        "0412-7256957","0212-9858996",profile_picture="/images/default.jpg",token=token_id2,mentor="Lobito",mentor_mail="lobito@reando.com")
        role_q3.users.append(user3)
        session.add(user3)

    with session_manager() as session:
        role_q4=session.query(Role).get(2)
        token_id4=serializer.dumps(str(3),salt="passing_id")
        user4=User("cristhian7bravo@gmail.com","Hola12#","Carlos","Perez",datetime.datetime.now(),"Venezolano","Hombre",\
        "single","venezuela","Caracas",1061,"El cafetal","USB",\
        "algo","algo","bachiller","bachiller","usb",\
        "0412-7256957","0212-9858996",profile_picture="/images/default.jpg",token=token_id4,mentor="Lobito",mentor_mail="lobito@reando.com")
        role_q4.users.append(user4)
        session.add(user4)

    with session_manager() as session:
        role_q7=session.query(Role).get(1)
        token_id7=serializer.dumps(str(4),salt="passing_id")
        user7=User("cristhian8bravo@gmail.com","Hola12#","Jaime","Bravo",datetime.datetime.now(),"Venezolano","Hombre",\
        "single","venezuela","Caracas",1061,"El cafetal","USB",\
        "algo","algo","bachiller","bachiller","usb",\
        "0412-7256957","0212-9858996",profile_picture="/images/default.jpg",token=token_id7,mentor="Lobito",mentor_mail="lobito@reando.com")
        role_q7.users.append(user7)
        session.add(user7)

    with session_manager() as session:
        role_q8=session.query(Role).get(1)
        token_id8=serializer.dumps(str(5),salt="passing_id")
        user8=User("cristhian9bravo@gmail.com","Hola12#","Andrea","Bravo",datetime.datetime.now(),"Venezolano","Hombre",\
        "single","venezuela","Caracas",1061,"El cafetal","USB",\
        "algo","algo","bachiller","bachiller","usb",\
        "0412-7256957","0212-9858996",profile_picture="/images/default.jpg",token=token_id8,mentor="Lobito",mentor_mail="lobito@reando.com")
        role_q8.users.append(user8)
        session.add(user8)

    with session_manager() as session:
        user=session.query(User).filter(User.email=="cristhian3bravo@gmail.com").update({User.active:True})
        user2=session.query(User).filter(User.email=="cristhian6bravo@gmail.com").update({User.active:True})
        user4=session.query(User).filter(User.email=="cristhian7bravo@gmail.com").update({User.active:True})
        user5=session.query(User).filter(User.email=="cristhian8bravo@gmail.com").update({User.active:True})
        user6=session.query(User).filter(User.email=="cristhian9bravo@gmail.com").update({User.active:True})

    print("Probando")
    return("Todo ok")

@application.route("/probando_ruta")
def ruta():

    return("1")

@application.route("/Evaluators")
def evaluators():
    return render_template('evaluators.html',avatar_url=current_user.profile_picture)

@application.route("/prueba1")
@admin_permission.require()
def prueba1():

    return("Lograste entrar ")

@application.route("/prueba2")
@estandar_permission.require()
def prueba2():

    return("Lograste entrar ")

@application.route("/load_admin")
def load_admin():

    with session_manager() as session:

        user=session.query(User).filter_by(email="cristhian3bravo@gmail.com").first()
        role=session.query(Role).get(2)
        try:
            role.users.append(user)
        except Exception as e:
            return(str(e))

        session.add(user)

        return("Creaste un evaluador")

@application.route("/mirando")
def mirando():

    with session_manager() as session:
        u=session.query(User).get(2)
        x=u.token
        return(x)

@application.route("/activateUsers")
def activate_user():

    with session_manager() as session:
        user=session.query(User).filter(User.id==4).update({User.active:True})
        return("El usuario fue activado")

@application.route("/probando_default",methods=["GET","POST"])
def default():

    form=ProbandoForm()

    if request.method=="POST":

        return("Lo lograste funciono")

    return render_template("probando_form.html", form=form)

@application.route("/notifications") ## notifications/<token>
def notifications():#token):

    # try:
    #     user_id = serializer.loads(token, salt="passing_id")
    #     user_id=int(user_id)
    #
    # except Exception as e:
    #     return("Ocurrio un error:" + str(e))

    with session_manager() as session:

        notifications=session.query(Notifications).filter_by(user_id=current_user.id).all()

        return render_template('notifications.html',avatar_url=current_user.profile_picture
)


@application.route("/edit_profile",methods=["GET","POST"])
def edit_user_profile():

    if request.method=="GET":

        with session_manager() as session:

            u=session.query(User).get(current_user.id)

            form=EditProfileForm(obj=u)

            return render_template("edit_profile.html",avatar_url=current_user.profile_picture,user=u,form=form)

    if request.method=="POST":

        form=EditProfileForm()

        if form.validate_on_submit:

            with session_manager() as session:

                u=session.query(User).get(current_user.id)

                form.populate_obj(u)

                session.add(u)

            return redirect(url_for('user_profile'))


@application.route("/probando_blob",methods=["GET","POST"])
def blob():

    class Email:

        def __init__(self,email=""):
            self.email=email

        def __repr__(self):

            return(str(["dummy_Data",self.email]))

    e1=Email()

    if request.method=="GET":

        form=ForgotPasswordForm(obj=e1)

        with session_manager() as session:

            data2=session.query(SaveFellow).get(1)

            return(str(data2.data.keys()))
            #request.form=data2.data
            #email=request.form['email']
            # return(str(form.__dict__))
            # return(email)
            # return(str(request.form))
            # print(data2.data)
            # data2.data.populate_obj(e1)
            #form.populate_obj(e1)
            #return(str(e1))

            #form=ForgotPasswordForm(obj=e1)

            return render_template("prueba_blob.html",form=form)

    else:

        form=ForgotPasswordForm()

        if request.method=="POST" and form.validate_on_submit:

        #data=pickle.dumps(request.form)
            return(str(form.__dict__))
            with session_manager() as session:
                return(str(request.form))
                p=SaveFellow(request.form)
                session.add(p)
            #data=jsonify(request.form)
            #return(str(request.form))
                return(str(p))
        # #p=Probando()
        # data=pickle.dumps(form)
        # return(p)




        # #data=jsonify(request.form)
        # #return(str(request.form))
        # return(data)

@application.route("/save_fellow",methods=["GET","POST"])
def save_fellow():

    if request.method=="POST":


        if request.form:

            with session_manager() as session:

                u=session.query(SaveFellow).filter_by(user_id=current_user.id)

                if u:

                    try:
                        u.delete()
                        session.flush()
                    except Exception as e:

                        return("Ocurrio un error inesperdado en 3171"+str(e))


                p=SaveFellow(request.form)
                user_data=session.query(User).get(current_user.id)
                user_data.user_save_fellow_data.append(p)
                session.add(p)
                return(str(p))

        else:

            return("Error en el ajax")





@application.route("/save_course", methods=["GET","POST"])
def save_course():

    ## Endpoint de salvar curso completamente funcional
    if request.method=="POST" :

        if request.form:

            with session_manager() as session:

                u=session.query(SaveCourse).filter_by(user_id=current_user.id)

                if u:

                    try:
                        u.delete()
                        session.flush()
                    except Exception as e:

                        return("Ocurrio un un error en la linea 3242" + str(e))


                p=SaveCourse(request.form)
                user_data=session.query(User).get(current_user.id)
                user_data.user_save_course_data.append(p)
                session.add(p)
                return(str(p))


        else:

            return("Error en el ajax")



@application.route("/create_pdf")
def create_pdf():

    pass

@application.route("/delete_all")
def delete_all():

    ## Funciona casi todo perfecto solo debo asociarlo al boton del dashboard
    ## y hacer la llamada por ajax

    from sqlalchemy.engine import reflection
    from sqlalchemy import create_engine
    from sqlalchemy.schema import (
        MetaData,
        Table,
        DropTable,
        ForeignKeyConstraint,
        DropConstraint,
        )
    from database import engine ,Base


    connection=engine.connect()
    trans=connection.begin()
    inspector= reflection.Inspector.from_engine(engine)

    metadata=MetaData()

    ## almaceno las tablas y las llaves foraneas
    tbs=[]
    all_fks=[]
    not_delete_tables=["log_applications","log_evaluadores","notifications","permisos","role","rolepermisos","users"]
    ## obtengo todos los nombres de las tablas
    for table_name in inspector.get_table_names():
        if table_name not in not_delete_tables:
            fks=[]
            ## itero sobre las tablas para obtener las propiedades
            ## las mismas se encuentran en forma de diccionario
            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(ForeignKeyConstraint((),(),name=fk['name']) )
            #     if not fk[]
            t=Table(table_name,metadata,*fks)
            tbs.append(t)
            all_fks.extend(fks)

    for fkc in all_fks:
        connection.execute(DropConstraint(fkc))

    for table in tbs:
        connection.execute(DropTable(table))

    trans.commit()

    Base.metadata.tables["curso"].create(bind = engine)
    Base.metadata.tables["courseBudgetItems"].create(bind = engine,checkfirst=True)
    Base.metadata.tables["courseCollaborators"].create(bind = engine,checkfirst=True)
    Base.metadata.tables["courseObjectives"].create(bind = engine,checkfirst=True)
    Base.metadata.tables["documentos_cursos"].create(bind = engine,checkfirst=True)
    Base.metadata.tables["evaluandocourses"].create(bind = engine,checkfirst=True)
    Base.metadata.tables["fellow"].create(bind = engine)
    Base.metadata.tables["evaluandofellows"].create(bind = engine)
    Base.metadata.tables["evaluation_courses"].create(bind = engine)
    Base.metadata.tables["evaluation_courses_backup"].create(bind = engine)
    Base.metadata.tables["evaluation_fellows"].create(bind = engine)
    Base.metadata.tables["evaluation_fellows_backup"].create(bind = engine)
    Base.metadata.tables["fellowActivities"].create(bind = engine)
    Base.metadata.tables["fellowDocuments"].create(bind = engine)
    Base.metadata.tables["fellowObjectives"].create(bind = engine)
    Base.metadata.tables["fellowbackup"].create(bind = engine)
    Base.metadata.tables["save_fellow"].create(bind = engine)
    Base.metadata.tables["save_course"].create(bind = engine)
    Base.metadata.tables["fellowActivitiesBackup"].create(bind = engine)
    Base.metadata.tables["fellowObjectivesBackup"].create(bind = engine)
    Base.metadata.tables["fellowDocumentsBackup"].create(bind = engine)
    #print(table_name)

    return(str("Succesfull"))

@application.route("/current_user")
def actual_user():

    return(current_user.email)
# @app.route("/load_evaluator")
# def load_evaluator()


##Creacion de PDF

@application.route("/generateCourse/<id>/<token>")
def  generateCoursePDF(id,token):

    role=3
    try:
        user_id = serializer.loads(token, salt="passing_id")
        user_id=int(user_id)

    except Exception as e:
        return("Ocurrio un error:" + str(e))

    url_id=str(id)

    form=ModalApprovedForm()


    # if current_user.role_id== 2:
    if role==2:

        with session_manager() as session:

            pending_fellow=session.query(evaluandofellows_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending_courses=session.query(evaluandocourses_table).filter_by(user_id=current_user.id,evaluation_status=False).count()
            pending=pending_fellow+pending_courses

            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            data=session.query(User,Curso).join(Curso, Curso.postulanteCurso_id==User.id).filter(Curso.id==url_id).first()
            course_objectives=session.query(CourseObjectives).filter(CourseObjectives.curso_id==url_id).all()
            course_BudgetItems=session.query(CourseBudgetsItems).filter(CourseBudgetsItems.curso_id==url_id).all()
            course_collaborators=session.query(CourseCollaborators).filter(CourseCollaborators.curso_id==url_id).all()
            evaluations=session.query(EvaluationCourses).filter_by(curso_id=url_id,evaluator_id=current_user.id).all()

            if data:

                d=data
                course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                hostName=d[1].hostName,hostAddress=d[1].hostAddress,coordName=d[1].coordName,coordTitle=d[1].coordTitle,\
                coordAffiliation=d[1].coordAffiliation,comDate=d[1].commDate,termDate=d[1].termDate,\
                description=d[1].courseDescription,organizationTraining=d[1].organizationTrainingDescription,\
                trainees=d[1].courseTrainees,output="Lorem ipsum, ipsum,ipsum",\
                objectives=course_objectives,budget=course_BudgetItems,\
                collaborators=course_collaborators,more=url_for('asign_evaluator_courses',id=url_id,token=token),evaluations=evaluations)

                rendered = render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course =course,\
                pending={"asignments":pending,"asigned_courses":pending_courses,"asigned_fellows":pending_fellow},\
                user={"name":current_user.name,"token":current_user.token},course_data={"id":url_id},form=form)

                pdf= pdfkit.from_string(rendered,False)

                response=make_response(pdf)
                response.headers['Content-Type']='application/pdf'
                response.headers['Content-Disposition']='inline;filename=output.pdf'
                return(response)

            else:
                return("No lograste entrar en data ")

    ##elif current_user.role == 3:
    elif role ==3:


        with session_manager() as session:

            ## Debo poner los links de los documentos mas abajo
            annex = dict(acceptanceLetter='#', fellowCV='#', mentorCV='#', medicalInform='#',
            recommendationLetter='#', infoForm='#', photo='#', vendorForm='#', fafDoc6='#', fafDoc7='#' )

            # data=session.query(User).get(user_id)
            # #curso=session.query(Curso).filter(Curso.postulanteCurso_id==user_id,Curso.id==url_id).all()
            # curso=session.query(Curso).filter(Curso.postulanteCurso_id==url_id).all()
            data=session.query(User,Curso).join(Curso, Curso.postulanteCurso_id==User.id).filter(Curso.id==url_id).first()
            course_objectives=session.query(CourseObjectives).filter(CourseObjectives.curso_id==url_id).all()
            course_BudgetItems=session.query(CourseBudgetsItems).filter(CourseBudgetsItems.curso_id==url_id).all()
            course_collaborators=session.query(CourseCollaborators).filter(CourseCollaborators.curso_id==url_id).all()
            evaluations=session.query(EvaluationCourses).filter_by(curso_id=url_id).all()

            ##aqui debo arreglar la data del querie para hacer la validacion de las evaluaciones
            if data:

                d=data
                course=dict(name= d[0].name,lastName=d[0].lastname,title=d[1].courseTitle,\
                hostName=d[1].hostName,hostAddress=d[1].hostAddress,coordName=d[1].coordName,coordTitle=d[1].coordTitle,\
                coordAffiliation=d[1].coordAffiliation,comDate=d[1].commDate,termDate=d[1].termDate,\
                description=d[1].courseDescription,organizationTraining=d[1].organizationTrainingDescription,\
                trainees=d[1].courseTrainees,output="Lorem ipsum, ipsum,ipsum",\
                objectives=course_objectives,budget=course_BudgetItems,\
                collaborators=course_collaborators,more=url_for('asign_evaluator_courses',id=url_id,token=d[1].user_candidateId),\
                evaluations=evaluations)

                ## Renderizamos el html con todas las variables necesarias
                rendered =render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course =course,user={"name":current_user.name,"token":current_user.token},\
                course_data={"id":url_id},form=form )

                ## Creamos el pdf
                pdf= pdfkit.from_string(rendered,False)
                return("LLegaste hasta despues del pdf")
                response=make_response(pdf)
                response.headers['Content-Type']='application/pdf'
                response.headers['Content-Disposition']='inline;filename=output.pdf'
                return(response)

            else:
                return("No lograste entrar en data ")

            return render_template('application_course.html',avatar_url=current_user.profile_picture,user_level = current_user.role_id, course=course,user={"name":current_user.name,"token":current_user.token},\
            course_data={"id":url_id},form=form) #current_user.role_id,  course =course)





if __name__ == '__main__':
    ## version deployment
    ## Usar esto a juro porque no funciona nada sin esto
    #application.run(debug=True)

    ## version development
    application.run(host="0.0.0.0",debug=True)
    #print(UPLOAD_FOLDER)
