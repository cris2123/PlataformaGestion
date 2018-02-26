from flask_wtf import Form
from wtforms import StringField , BooleanField, TextField,\
PasswordField,DateField, RadioField,SelectField,IntegerField,TextAreaField
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import FormField ,SubmitField
from wtforms.fields.html5 import TelField
from wtforms.validators import DataRequired, InputRequired,Email,EqualTo
from wtforms.validators import Regexp
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets import TextArea

from models import CourseObjectives,CourseBudgetsItems, CourseCollaborators,FellowObjectives,\
FellowActivities



class LoginForm(Form):

    email= StringField("email",[InputRequired("ingresa direccion de correo valida"),Email()])
    password= PasswordField("password",[InputRequired(),Regexp(message=""" El password debe tener
    minimo 6 digitos,con caracter especial,mayúscula, minúscula y un número""",\
    regex=r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-,_,$,&,%,*,!,<,>,",?,@,#,^,=,+]).{6,20}')] )
    remember_me=BooleanField("Remember me",default=False)

class ForgotPasswordForm(Form):

	email= StringField("email",[InputRequired("Ingresa direccion de correo valida"),Email()])

class RecoverPasswordForm(Form):

    password= PasswordField("New Password",\
    [InputRequired(),EqualTo('re_password',\
        message="Las contraseñas deben coincidir"),Regexp(message="""El password debe tener
        minimo 6 digitos,con caracter especial,mayúscula, minúscula y un número""",\
        regex=r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-,_,$,&,%,*,!,<,>,",?,@,#,^,=,+]).{6,20}')] )
    re_password= PasswordField("Retype new password")

class RegisterForm(Form):

    email= StringField("email",[InputRequired("Ingresa direccion de correo valida"),Email()])
    password= PasswordField("password",\
    [InputRequired(),EqualTo('re_password',\
        message="Las contraseñas deben coincidir"),Regexp(message="""El password debe tener
        minimo 6 digitos,con caracter especial,mayúscula, minúscula y un número""",\
        regex=r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[-,_,$,&,%,*,!,<,>,",?,@,#,^,=,+]).{6,20}')] )
    re_password= PasswordField("Repite el password")
    name=StringField("Nombre",[InputRequired("Ingresa tu nombre")])
    lastname=StringField("Apellido",[InputRequired("Ingresa tu apellido")])
    birth_date=DateField("Date of Birth (YYYY-MM-DD)",\
    	[InputRequired("Ingresa la fecha de nacimiento en el formato año-mes-dia")],\
    	format="%Y-%m-%d")
    #
    # ##Datos personales
    citizenship=StringField("Nacionalidad",[InputRequired("Coloca tu nacionalidad")])
    gender=RadioField("Genero",[InputRequired("Campo Requerido")],choices=[("Hombre","Male"),("Mujer","Female")])
    marital_status=StringField("Estado Civil",[InputRequired("Coloca tu estado civil")])
    profile_picture=FileField('Profile Picture (Not required)',[FileAllowed(['jpg','png'],'Solo imagenes con formato jpg o png')])

    # ## direccion normal
    country= StringField('País',[InputRequired("Ingresa tu pais")])
    city= StringField('Ciudad',[InputRequired("Ingresa tu ciudad")])
    zip_code=IntegerField("Codigo postal",[InputRequired("Tines que ingresar un numero")])
    address=StringField('Direccion',[InputRequired("Ingresa tu direccion")])
    phonenumber=TelField("Numero de telefono",[InputRequired("Ingresa un numero de telefono valido")])
    cellphone=TelField("Numero de celular",[InputRequired("Ingresa un numero de telefono valido")])

    ## institucion
    institution= StringField('Institución',[InputRequired("Ingresa el nombre de tu institucion")])
    faculty= StringField('Facultad',[InputRequired("Ingresa la facultad a la que perteneces")])
    section= StringField('Sección específica',[InputRequired("Ingresa la seccion-division a la que perteneces")])
    mentor= StringField('Mentor',[InputRequired("Ingresa el nombre y appelido de tu mentor")])
    mentor_mail = StringField('E-mail de Mentor',[InputRequired("Ingresa el correo electronico de tu mentor")])

    ## Perfil cientifico
    max_academic_level=StringField('Máximo nivel académico alcanzado',[InputRequired("Máximo nivel académico alcanzado")])
    current_academic_level=StringField('Nivel actual de estudio',[InputRequired("Ingresa tu nivel de estudio actual")])
    work_place=StringField('Lugar de trabajo/investigación',[InputRequired("Investigación actual")])
    ##MiniForm es para el form de evaluacion de curso

class EditProfileForm(Form):

    email= StringField("email",[InputRequired("Ingresa direccion de correo valida"),Email()])

    name=StringField("Nombre",[InputRequired("Ingresa tu nombre")])
    lastname=StringField("Apellido",[InputRequired("Ingresa tu apellido")])
    birth_date=DateField("Date of Birth (YY-MM-DD)",\
    	[InputRequired("Ingresa la fecha de nacimiento en el formato año-mes-dia")],\
    	format="%Y-%m-%d")

    # ##Datos personales
    citizenship=StringField("Nacionalidad",[InputRequired("Coloca tu nacionalidad")])
    gender=RadioField("Genero",[InputRequired("Campo Requerido")],choices=[("Hombre","Male"),("Mujer","Female")])
    marital_status=StringField("Estado Civil",[InputRequired("Coloca tu estado civil")])
    profile_picture=FileField('Profile Picture (Not required)',[FileAllowed(['jpg','png'],'Solo imagenes con formato jpg o png')])

    # ## direccion normal
    country= StringField('País',[InputRequired("Ingresa tu pais")])
    city= StringField('Ciudad',[InputRequired("Ingresa tu ciudad")])
    zip_code=IntegerField("Codigo postal",[InputRequired("Tines que ingresar un numero")])
    address=StringField('Direccion',[InputRequired("Ingresa tu direccion")])
    phonenumber=TelField("Numero de telefono",[InputRequired("Ingresa un numero de telefono valido")])
    cellphone=TelField("Numero de celular",[InputRequired("Ingresa un numero de telefono valido")])

    ## institucion
    institution= StringField('Institución',[InputRequired("Ingresa el nombre de tu institucion")])
    faculty= StringField('Facultad',[InputRequired("Ingresa la facultad a la que perteneces")])
    section= StringField('Sección específica',[InputRequired("Ingresa la seccion-division a la que perteneces")])

    ## Perfil cientifico
    max_academic_level=StringField('Máximo nivel académico alcanzado',[InputRequired("Máximo nivel académico alcanzado")])
    current_academic_level=StringField('Nivel actual de estudio',[InputRequired("Ingresa tu nivel de estudio actual")])
    work_place=StringField('Lugar de trabajo/investigación',[InputRequired("Investigación actual")])
    ##MiniForm es para el form de evaluacion de curso

#Course or Fellow Objectives
class ObjectiveForm(NoCsrfForm):
    objective_item = StringField('Objective Name')

# Fellow Activities
class ActivityForm(NoCsrfForm):
    activity_item = StringField('Activity Name')

# - - - Forms - - -
class BudgetForm(NoCsrfForm):
    # this forms is never exposed so we can use the non CSRF version jeje
    budget_desc = StringField('Item', validators=[DataRequired()])
    budget_value = StringField('USD', validators=[DataRequired()])

class CollaboratorForm(NoCsrfForm):
    coll_name = StringField('Full Name')
    coll_position = StringField('Position')
    coll_institution = StringField()
    coll_phone = StringField()
    coll_fax = StringField()
    coll_email = StringField()
    coll_area = StringField()
    coll_CV = FileField()

##CourseForm es para el form de postulacion de un curso
class CourseForm(Form):

    priority=RadioField("Priority",choices=[("1","Emerging and neglected human, animal and plant diseases"),("2","Environmental microbiology: Metagenomics as a bioprospection tool for bioremediation"),\
    ("3","Renewable sources of energy (industrial biotechnology)")])
    courseTitle = StringField(u'Text')
    hostName = StringField(u'Text')
    hostAddress = StringField(u'Text')
    coordName= StringField(u'Text')
    coordTitle = StringField(u'Text')
    coordAffiliation = StringField(u'Text')
    #Pilas aqui con el formato, porque en HTML es mm-dd-yy (YO copie tu implementacion en Register_form)
    commDate=DateField("Expected Commencement Date (YY-MM-DD)",\
		[InputRequired("Please specify an Expected Commencement Date for your Training Course")],\
		format="%Y-%m-%d")
    termDate=DateField("Expected Termination Date (YY-MM-DD)",\
		[InputRequired("Please specify an Expected Termination Date for your Training Course")],\
		format="%Y-%m-%d")
    destination= StringField(u'Text')
    courseObjectives = FieldList( FormField( ObjectiveForm, default = lambda: CourseObjectives() ) )
    courseDescription = StringField(u'Text', widget=TextArea())
    organizationTrainingDescription = StringField(u'Text', widget=TextArea())
    courseCollaborators = FieldList(FormField(CollaboratorForm, default = lambda:CourseCollaborators() ) )
    expectedOutput = StringField(u'Text', widget=TextArea())
    courseTrainees = StringField(u'Text', widget=TextArea())
    courseBudgetItems = FieldList(FormField(BudgetForm, default = lambda:CourseBudgetsItems()) )
    submit = SubmitField('Submit')
    fundingSource = StringField(u'Text')
    fundingSourceScore = IntegerField(u'Text')   #numerico
    counterpartFund = StringField(u'Text')
    counterpartFundScore = IntegerField(u'Text') #numerico

##FellowForm es para el form de postulacion de un fellow
class FellowForm(Form):
    priority=RadioField("Priority",choices=[("1","Emerging and neglected human, animal and plant diseases"),("2","Environmental microbiology: Metagenomics as a bioprospection tool for bioremediation"),\
    ("3","Renewable sources of energy (industrial biotechnology)")])
    fellowTitle = StringField(u'Text')
    destination = StringField(u'Text')
    generalObjective = StringField(u'Text', widget=TextArea())
    fellowObjectives = FieldList(FormField(ObjectiveForm, default= lambda:FellowObjectives()) )
    justification = StringField(u'Text', widget=TextArea())
    fellowActivities = FieldList(FormField(ActivityForm,default=lambda:FellowActivities() ))
    methodology = StringField(u'Text', widget=TextArea())
    workingPlan = StringField(u'Text', widget=TextArea())
    acceptanceLetter = FileField('Acceptance Letter From Host Institution signed by Mentor')
    fellowCV  = FileField('Fellow CV')
    mentorCV  = FileField('Mentor CV')
    recommendationLetter  = FileField('Recommendation Letter from supervisor or mentor')
    infoForm  = FileField('Completed and signed applicant personal information form')
    photo  = FileField('Fellow candidate photo o dices fellow')
    vendorForm  = FileField('Vendor Form from Host Institution *')
    fafDoc6  = FileField('Signed and stamped by Host Institution the (FAF_Doc_6) in acceptance of conditions of grant by applicant')
    fafDoc7 = FileField('Conditions acceptance of grant by Director of the applicant`s institution (FAF_Doc_7) Signed and stamped')
    medicalInform  = FileField('Medical inform (FAF_Doc_8) Signed and stamped')
    hostInstitution = StringField(u'Text')
    commDate=DateField("Expected Commencement Date (YY-MM-DD)",\
		[InputRequired("Please specify an Expected Commencement Date for your Fellow Plan")],\
		format="%Y-%m-%d")
    termDate=DateField("Expected Termination Date (YY-MM-DD)",\
		[InputRequired("Please specify an Expected Termination Date for your Fellow Plan")],\
		format="%Y-%m-%d")
    criteria = StringField(u'Text', widget=TextArea())

class ModalRoleForm(Form):
    roles=RadioField("Roles",[InputRequired()],choices=[("Standard","Standard"),("Evaluator","Evaluator"),("Assistant","Assistant")])

class MiniForm(Form):
    objectiveComment = StringField(u'Text', widget=TextArea())
    descriptionComment = StringField(u'Text', widget=TextArea())
    collaboratorsComment = StringField(u'Text', widget=TextArea())
    budgetComment = StringField(u'Text', widget=TextArea())
    traineesComment = StringField(u'Text', widget=TextArea())
    finalComment = StringField(u'Text', widget=TextArea())
    overallQualification = RadioField("Score",[InputRequired("Campo Requerido")],choices=[("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],default="1")
    # referee = StringField("Test")

##MiniForm2 es para el form de evaluacion de fellow
class MiniForm2(Form):
    previousInvestigationScore = RadioField("Score",choices=[("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],default="1")
    previousInvestigation = StringField(u'Text', widget=TextArea())
    currentInvestigationScore = RadioField("Score",choices=[("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],default="1")
    currentInvestigation = StringField(u'Text', widget=TextArea())
    purposeApplicationScore  = RadioField("Score",choices=[("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],default="1")
    purposeApplication = StringField(u'Text', widget=TextArea())
    otherTrainingCoursesScore = RadioField(u'Text',choices=[("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],default="1")
    otherTrainingCourses = StringField(u'Text', widget=TextArea())
    finalReviewScore = RadioField("Score",choices=[("Aprobado","Approved"),("Rechazado","Denied")],default="Rechazado")
    finalReview = StringField(u'Text', widget=TextArea())

class ObjectiveForm2(NoCsrfForm):
    objective_item = StringField('Objective item')
    objective_field = StringField('Objective field')

class ModalApprovedForm(Form):

    Approved_budget=StringField('Full Name')

class MiniCourse(Form):
    courseObjectives = FieldList( FormField( ObjectiveForm, default = lambda: CourseObjectives() ) )

    #courseObjectives = FieldList(FormField(ObjectiveForm) )
    #courseBudgetItems = FieldList("Budgets",FormField(BudgetForm), default = "1")
    #courseCollaborators = FieldList("colaboradores",FormField(CollaboratorForm), default="1")
    submit = SubmitField('Submit')

class ProbandoForm(Form):

    previousInvestigationScore = RadioField("Score",choices=[("1","1"),("2","2"),("3","3"),("4","4"),("5","5")],default="1")
