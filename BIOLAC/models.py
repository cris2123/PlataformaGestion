# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import  *
from datetime import datetime
from flask_login import UserMixin
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy_utils import PhoneNumber

#__all__=['User']

rolepermisos_table=Table('rolepermisos', Base.metadata,
	Column('role_id',Integer,ForeignKey('role.id')),
	Column('permisos_id',Integer, ForeignKey('permisos.id',onupdate="CASCADE", ondelete="CASCADE")) )

evaluandofellows_table=Table('evaluandofellows', Base.metadata,
	Column('user_id',Integer,ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE")),
	Column('fellow_id',Integer, ForeignKey('fellow.id',onupdate="CASCADE", ondelete="CASCADE")),
	Column('evaluation_status',Boolean,default=False) )

evaluandocourses_table=Table('evaluandocourses', Base.metadata,
	Column('user_id',Integer,ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE")),
	Column('curso_id',Integer, ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE")),
	Column('evaluation_status',Boolean,default=False) )

class Role(Base):

	__tablename__ = 'role'

	id= Column(Integer(),primary_key=True)
	name= Column(String(15),nullable=False)
	description= Column(String(80),nullable=False)
	users =relationship("User", backref=backref('role'))

	## Relacion de mucho a mucho con las tablas de role y permisos
	permisos= relationship(
		"Permisos",
		secondary=rolepermisos_table,
		backref="role")

	def __init__(self,name,description):

		self.name=name
		self.description=description

	def __repr__(self):

		return(str(['role',self.name,self.description]))

class Permisos(Base):

	__tablename__= 'permisos'

	id=Column(Integer(),primary_key=True)
	name= Column(String(15))
	description=Column(String(80))

	def __init__(self,name,description):

		self.name=name
		self.description=description

	def __repr__(self):

		return(str(['permisos',self.name,self.description]))

class User(Base,UserMixin):

    __tablename__ = 'users'

    ## Informacion personal
    id=Column(Integer(),primary_key=True)
    email= Column(String(80),unique=True)
    name= Column(String(20),nullable=False)
    lastname=Column(String(20),nullable=False)
    birth_date= Column(DateTime(),nullable=False)
    citizenship= Column(String(25),nullable=False)
    gender= Column(String(25),nullable=False)
    marital_status= Column(String(15),nullable=False)
    profile_picture=Column(String(100),nullable=True)
    country=Column(String(20),nullable=False)
    city=Column(String(20),nullable=False)
    zip_code=Column(Integer(),nullable=False)
    address=Column(String(50),nullable=False)
    phonenumber=Column(String(25),nullable=False)
    cellphone=Column(String(25),nullable=False)
    institution=Column(String(35),nullable=False)
    faculty=Column(String(20),nullable=False)
    section=Column(String(20),nullable=False)
    max_academic_level=Column(String(20),nullable=False)
    current_academic_level=Column(String(20),nullable=False)
    work_place=Column(String(30),nullable=False)
    lastSeen=Column(DateTime(),default=datetime.now)
    token=Column(String(100))
    evaluated_applications=Column(Integer(),default=0)

    ## mentor data
    mentor=Column(String(20),nullable=False)
    mentor_mail=Column(String(20),nullable=False)

    ################## EXTRA FEATURES ######################################
    ## Composite type para los usuarios
    #phonenumber = composite( PhoneNumber, _phonenumber,country_code)
    ########################################################################

    ## Datos necesarios par el funcionamiento de la plataforma
    possible_evaluator= Column(Boolean(),default=False)
    active= Column(Boolean(),default=False)

    ## Relaciones con otras tablas
    role_id=  Column(Integer(),ForeignKey('role.id',onupdate="CASCADE", ondelete="CASCADE"))

    ## password hashing
    password=Column(String(100),nullable=False)

    ##relacion con las tablas de cursos
    curso= relationship("Curso", cascade="save-update, delete", backref=backref('users'))

    ## backup

    #curso= relationship("CursoBackup", cascade="save-update, delete", backref=backref('users'))

    completed_users_evaluations= relationship("LogEvaluadores",cascade="save-update, delete", backref=backref('users'))

    ## relacion con la tabla de notificaciones
    notifications= relationship("Notifications",cascade="save-update, delete", backref=backref('users'))

    user_save_fellow_data = relationship("SaveFellow",cascade="save-update, delete", backref=backref('users'))

    user_save_course_data = relationship("SaveCourse",cascade="save-update, delete", backref=backref('users'))

    evaluados= relationship(
    	"Fellow",
    	secondary=evaluandofellows_table,
    	backref="users")

    evaluando_courses= relationship(
    	"Curso",
    	secondary=evaluandocourses_table,
    	backref="users_evaluando")

    ## metodos para de la clase de usuario

    def __init__(self, email, password, name, lastname, birth_date, citizenship,\
    	gender, marital_status, country, city, zip_code, address,\
    	institution, faculty, section, max_academic_level, current_academic_level,\
    	work_place, cellphone, phonenumber ,profile_picture,token="",evaluated_applications="0",\
    	mentor="",mentor_mail=""):

    	self.email= email
    	self.password= generate_password_hash(password)
    	self.name=name
    	self.lastname=lastname
    	self.birth_date=birth_date
    	self.citizenship=citizenship
    	self.gender=gender
    	self.marital_status=marital_status
    	self.country=country
    	self.city=city
    	self.zip_code=zip_code
    	self.address=address
    	self.institution=institution
    	self.faculty=faculty
    	self.section=section
    	self.max_academic_level=max_academic_level
    	self.current_academic_level=current_academic_level
    	self.work_place=work_place
    	self.cellphone=cellphone
    	self.phonenumber=phonenumber
    	self.profile_picture=profile_picture
    	self.token=token
    	self.mentor=mentor
    	self.mentor_mail=mentor_mail



    ## Definiendo los metodos necesarios para flask-login
    def is_active(self):

        return(self.active)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def _get_password(self):
    	return self.password


    ################## EXTRA FEATURES ######################################
    # def _set_password(self, password):
    # 	self._password = generate_password_hash(password)
    # Hide password encryption by exposing password field only.
    #password = synonym('_password', descriptor=property(_get_password, _set_password))
    #########################################################################

    def check_password(self, password):
    	if self.password is None:
    		return False
    	return check_password_hash(self.password, password)

    ## Representacion de la clase usuario
    def __repr__(self):

        return(str(['user',

    	self.email,
    	self.password,
    	self.name,
    	self.lastname,
    	self.birth_date,
    	self.citizenship,
    	self.gender,
    	self.marital_status,
    	self.profile_picture,
    	self.country,
    	self.city,
    	self.zip_code,
    	self.address,
    	self.institution,
    	self.faculty,
    	self.section,
    	self.max_academic_level,
    	self.current_academic_level,
    	self.work_place,
    	self.cellphone,
    	self.phonenumber,
    	self.profile_picture,
    	self.mentor,
    	self.mentor_mail,
    	self.token]))



class Curso(Base):

	__tablename__='curso'
	id=Column(Integer(),primary_key=True)
	priority=Column(String(3))
	courseTitle=Column(String(80))
	hostName=Column(String(80))
	destination=Column(String(80))
	hostAddress=Column(String(80))
	coordName=Column(String(80))
	coordTitle=Column(String(80))
	coordAffiliation=Column(String(80))
	commDate=Column(DateTime(),nullable=False)
	termDate=Column(DateTime(),nullable=False)
	courseDescription=Column(String(2000))
	organizationTrainingDescription=Column(String(2000))
	courseTrainees=Column(String(2000))

	## datos extra
	fundingSource = Column( String(500) )
	fundingSourceScore = Column(Integer(),nullable=False)
	counterpartFund = Column(String(500),nullable=False)
	counterpartFundScore = Column(Integer(),nullable=False)

	## Flags para conocer el status del curso

	# status_aprobado=Column(Boolean(),default=False)
	status_aprobado=Column(String(10),default="Pending")
	status_revisado=Column(Boolean(),default=False) ## En evaluacion
	revisiones_completadas=Column(Integer(),default=0)
	user_candidateId=Column(String(200),nullable=False)
	user_candidateName=Column(String(200))
	user_candidateLastName=Column(String(200))
	user_candidateEmail=Column(String(100),nullable=False)
	aprove_budget=Column(String(20))


	## Id del usuario que postulo el curso
	postulanteCurso_id= Column(Integer(),ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	## Relacion con la tabla de documentos del curso
	cursoDocs = relationship("DocumentosCursos", cascade="save-update,delete",backref=backref('curso'))

	## Relacion con la tabla de objetivos del curso
	courseObjectives=relationship("CourseObjectives", cascade="save-update, delete", backref=backref('curso'))

	## Relacion con la tabla de colaboradores de los cursos
	courseCollaborators=relationship("CourseCollaborators",cascade="save-update,delete", backref=backref('curso'))

	## Relaciona con la tabla de budget Items
	courseBudgetItems=relationship("CourseBudgetsItems", cascade="save-update, delete", backref=backref('curso'))

	## relacion con la tabla de Evaluators del curso
	course_evaluations=relationship("EvaluationCourses", cascade="save-update, delete", backref=backref('curso'))

	## relacion con la tabla de Evaluators del curso
	course_evaluations_backup=relationship("EvaluationCoursesBackup", cascade="save-update, delete", backref=backref('curso'))

	# Para debugging agregar una manera de setear los flags en la instanciacion
	# Puedo ponerlo por default y cuando lo instancio ponerlo True

	def __init__(self, courseTitle="", hostName="", hostAddress="", coordName="", coordTitle="",\
	 	coordAffiliation="", commDate="", termDate="", courseDescription="", organizationTrainingDescription="",\
		courseTrainees="",priority=False,destination="",user_candidateId="",user_candidateEmail="",\
		user_candidateName="",user_candidateLastName="",aprove_budget="Pending",fundingSource="",\
		fundingSourceScore="",counterpartFund="",counterpartFundScore=""):

		self.priority=priority
		self.courseTitle=courseTitle
		self.hostName=hostName
		self.hostAddress=hostAddress
		self.coordName=coordName
		self.coordTitle=coordTitle
		self.coordAffiliation=coordAffiliation
		self.commDate=commDate
		self.termDate=termDate
		self.courseDescription=courseDescription
		self.organizationTrainingDescription=organizationTrainingDescription
		self.courseTrainees=courseTrainees
		self.user_candidateId=user_candidateId
		self.user_candidateEmail=user_candidateEmail
		self.user_candidateName=user_candidateName
		self.user_candidateLastName=user_candidateLastName
		self.aprove_budget=aprove_budget
		self.fundingSource=fundingSource
		self.fundingSourceScore=fundingSourceScore
		self.counterpartFund=counterpartFund
		self.counterpartFundScore=counterpartFundScore



	def __repr__(self):

		return(str(['cursos',\

		self.priority,
		self.courseTitle,
		self.hostName,
		self.hostAddress,
		self.coordName,
		self.coordTitle,
		self.coordAffiliation,
		self.commDate,
		self.termDate,
		self.courseDescription,
		self.organizationTrainingDescription,
		self.user_candidateId,
		self.user_candidateEmail,
		self.user_candidateName,
		self.user_candidateLastName,
		self.courseTrainees,
		self.fundingSource,
		self.fundingSourceScore,
		self.counterpartFund,
		self.counterpartFundScore,
		self.aprove_budget]))


class CourseObjectives(Base):

	__tablename__='courseObjectives'
	id=Column(Integer(),primary_key=True)
	objective_item=Column(String(200),nullable=False)

	## Llave  foranea con el curso donde se postula esta data
	curso_id=Column(Integer(),ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,objective_item=""):

		self.objective_item= objective_item

	def __repr__(self):

		return(str(['coursesObjectives',self.objective_item]))


class CourseBudgetsItems(Base):

	__tablename__='courseBudgetItems'
	id=Column(Integer(),primary_key=True)
	budget_desc=Column(String(120))
	budget_value=Column(String(10))

	## Llave  foranea con el curso donde se postula esta data
	curso_id=Column(Integer(),ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,budget_desc="",budget_value=""):

		self.budget_desc=budget_desc
		self.budget_value=budget_value

	def __repr__(self):

		return(str(['coursesBudgetItems',self.budget_desc,self.budget_value]))

class CourseCollaborators(Base):

	__tablename__='courseCollaborators'
	id=Column(Integer(),primary_key=True)
	coll_name=Column(String(20))
	coll_position=Column(String(20))
	coll_institution=Column(String(30))
	coll_phone=Column(String(20))
	coll_email=Column(String(70))
	coll_area=Column(String(15))
	coll_cv=Column(String(100))

	## Llave  foranea con el curso donde se postula esta data
	curso_id=Column(Integer(),ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,coll_name="",coll_position="",coll_institution="",coll_phone="",\
		coll_email="",coll_area="",coll_cv="Probando path"):

		self.coll_name=coll_name
		self.coll_position=coll_position
		self.coll_institution=coll_institution
		self.coll_phone=coll_phone

		self.coll_email=coll_email
		self.coll_area=coll_area
		self.coll_cv=coll_cv

	def __repr__(self):

		return(str(['coursescollaborators',self.coll_name,\
		self.coll_position,
		self.coll_institution,
		self.coll_phone,

		self.coll_email,
		self.coll_area,
		self.coll_cv]))

class DocumentosCursos(Base):

	__tablename__= 'documentos_cursos'

	id= Column(Integer(),primary_key=True)
	name = Column(String(80),nullable=True)
	path= Column(String(100))
	hashed_name= Column(String(100))
	fecha=Column(DateTime(),default=datetime.now)
	curso_id= Column(Integer(),ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self,name,path,hashed_name):

		self.name=name
		self.path=path
		self.hashed_name=hashed_name


	def __repr__(self):

		return(str['Documentos Cursos',self.nombre,self.hashed_name,
		self.fecha,
		self.relative_path])

class EvaluationCourses(Base):

	__tablename__='evaluation_courses'
	id=Column(Integer(),primary_key=True)
	objectiveComment = Column(Text(2000),nullable=False)
	descriptionComment = Column(Text(2000),nullable=False)
	collaboratorsComment = Column(Text(2000),nullable=False)
	budgetComment = Column(Text(2000),nullable=False)
	traineesComment = Column(Text(2000),nullable=False)
	finalComment = Column(Text(2000),nullable=False)
	overallQualification = Column(Integer(),nullable=False)


	## Campos para facilitar los queries y hacer mejores filtrajes
	evaluator_id=Column(Integer(),nullable=False)
	evaluator_name=Column(String(50))
	evaluator_email=Column(String(80))
	evaluator_lastName=Column(String(30))
	evaluated_date=Column(DateTime(),default=datetime.now)

	## llave foranea para la evaluacion de las tablas
	curso_id= Column(Integer(),ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self,objectiveComment,descriptionComment,collaboratorsComment,budgetComment,\
	traineesComment,finalComment,overallQualification,evaluator_id,\
	evaluator_name='',evaluator_email="",evaluator_lastName=""):

		self.objectiveComment=objectiveComment
		self.descriptionComment=descriptionComment
		self.collaboratorsComment=collaboratorsComment
		self.budgetComment=budgetComment
		self.traineesComment=traineesComment
		self.finalComment=finalComment
		self.overallQualification=overallQualification
		self.evaluator_id=evaluator_id
		self.evaluator_name=evaluator_name
		self.evaluator_email=evaluator_email
		self.evaluator_lastName=evaluator_lastName

	def __repr__(self):

	    return(str(['EvaluationCourses',

		self.objectiveComment,
		self.descriptionComment,
		self.collaboratorsComment,
		self.budgetComment,
		self.traineesComment,
		self.finalComment,
		self.overallQualification,
		self.evaluator_lastName,
		self.evaluator_id,
		self.evaluator_email,
		self.evaluator_name]))

class EvaluationCoursesBackup(Base):

	__tablename__='evaluation_courses_backup'

	id=Column(Integer(),primary_key=True)
	objectiveComment = Column(Text(2000))
	descriptionComment = Column(Text(2000))
	collaboratorsComment = Column(Text(2000))
	budgetComment = Column(Text(2000))
	traineesComment = Column(Text(2000))
	finalComment = Column(Text(2000))
	overallQualification = Column(Integer())


	evaluator_id=Column(Integer(),nullable=False)
	## Campos para facilitar los queries y hacer mejores filtrajes
	evaluator_name=Column(String(50))
	evaluated_date=Column(DateTime(),default=datetime.now)

	## llave foranea para la evaluacion de las tablas
	curso_id= Column(Integer(),ForeignKey('curso.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self,objectiveComment="",descriptionComment="",collaboratorsComment="",budgetComment="",\
	traineesComment="",finalComment="",overallQualification="",\
	evaluator_name='',evaluator_id=""):

		self.objectiveComment=objectiveComment
		self.descriptionComment=descriptionComment
		self.collaboratorsComment=collaboratorsComment
		self.budgetComment=budgetComment
		self.traineesComment=traineesComment
		self.finalComment=finalComment
		self.overallQualification=overallQualification
		self.evaluator_id=evaluator_id
		self.evaluator_name=evaluator_name

	def __repr__(self):

	    return(str(['EvaluationCoursesBackup',

		self.objectiveComment,
		self.descriptionComment,
		self.collaboratorsComment,
		self.budgetComment,
		self.traineesComment,
		self.finalComment,
		self.overallQualification,
		self.evaluator_id,
		self.evaluator_name]))

class Fellow(Base):

	__tablename__="fellow"

	## Debo agregarle nombre al postulante
	id = Column(Integer(),primary_key=True, autoincrement=False)

	## Datos basicos del postulante
	name= Column(String(30)) ## nombre del postulante
	lastName=Column(String(30))
	citizenship=Column(String(30))

	## Datos especificios del fellow
	priority = Column(String(2))
	fellowTitle = Column(String(40))
	destination= Column(String(50))
	generalObjective= Column(String(300))
	justification= Column(String(300))
	methodology = Column(String(300)) ## nombre de la institucion
	workingPlan = Column(String(400))
	fellow_userTokenId=Column(String(200))
	fellow_candidateEmail=Column(String(80))

	#modificaciones para el fellow form
	criteria=Column(String(2000))
	hostInstitution=Column(String(50))
	commDate=Column(DateTime(),nullable=False)
	termDate=Column(DateTime(),nullable=False)
	mentor_p=Column(String(60),nullable=False)
	mentor_pEmail=Column(String(60),nullable=False)


	## Flags necesarias para crear la funcionalidad de la aplicacion
	status_aprobado= Column(String(10),default=False)
	creation_date= Column(DateTime(),nullable=False, default=datetime.now)
	revisiones_completadas= Column(Integer(),nullable=True)
	evaluators_asignedCount=Column(Integer(),nullable=False)

	## Relacion foranea con la tabla de objetivos de cada Fellow
	fellowObjectives= relationship("FellowObjectives", cascade="save-update, delete", backref=backref('fellow'))

	## Relacion foranea con la tabla de Actividades de cada fellow
	fellowActivities= relationship("FellowActivities", cascade="save-update, delete", backref=backref('fellow'))

	## Relacion con la tabla de documentos del postulante
	fellowDocs = relationship("FellowDocuments",cascade="save-update, delete", backref=backref('fellow'))

	## Relacion con la tabla de las evaluaciones realizadas por los fellows
	fellow_evaluations = relationship("EvaluationFellows",cascade="save-update, delete", backref=backref('fellow'))

	## Relacion con la tabla del estad odel salvar las evaluaciones de los usuarios
	fellow_evaluations_backup = relationship("EvaluationFellowsBackup",cascade="save-update, delete", backref=backref('fellow'))



	def __init__(self,id=0,name="",lastName="",citizenship="",priority=False,\
	fellowTitle="",destination="",generalObjective="",justification="",\
	methodology="",workingPlan="",status_aprobado="Pending",revisiones_completadas= 0,fellow_userTokenId="",\
	fellow_candidateEmail="",evaluators_asignedCount="",criteria="",hostInstitution="",\
	commDate="",termDate="",mentor_p="",mentor_pEmail=""):

		self.id=id
		self.name=name
		self.lastName
		self.citizenship
		self.priority=priority
		self.fellowTitle=fellowTitle
		self.destination=destination
		self.generalObjective=generalObjective
		self.justification=justification
		self.methodology=methodology
		self.workingPlan=workingPlan
		self.status_aprobado=status_aprobado
		self.revisiones_completadas=revisiones_completadas
		self.fellow_userTokenId=fellow_userTokenId
		self.fellow_candidateEmail=fellow_candidateEmail
		self.evaluators_asignedCount=evaluators_asignedCount
		self.criteria=criteria
		self.commDate=commDate
		self.termDate=termDate
		self.hostInstitution=hostInstitution

	def __repr__(self):

		return(str(['fellow',self.id,self.name,self.lastName,self.citizenship,self.priority,\
		self.fellowTitle,
		self.destination,
		self.generalObjective,
		self.justification,
		self.methodology,
		self.workingPlan,
		self.status_aprobado,
		self.criteria,
		self.commDate,
		self.termDate,
		self.hostInstitution,
		self.revisiones_completadas]))


class FellowObjectives(Base):

	__tablename__= 'fellowObjectives'

	id=Column(Integer(),primary_key=True)
	objective_item=Column(String(200),nullable=False)

	## Llave  foranea con el curso donde se postula esta data
	fellow_id=Column(Integer(),ForeignKey('fellow.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,objective_item=""):

		self.objective_item= objective_item

	def __repr__(self):

		return(str(['fellowObjectives',self.objective_item]))

class FellowActivities(Base):

	__tablename__= 'fellowActivities'

	id=Column(Integer(),primary_key=True)
	activity_item=Column(String(100),nullable=False)

	## Llave  foranea con el curso donde se postula esta data.
	fellow_id=Column(Integer(),ForeignKey('fellow.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,activity_item=""):

		self.activity_item= activity_item

	def __repr__(self):

		return(str(['fellowActivities',self.activity_item]))

class FellowDocuments(Base):

	__tablename__= 'fellowDocuments'

	id= Column(Integer(),primary_key=True)
	name=Column(String(100))
	path= Column(String(100))
	hashed_name= Column(String(100))
	fecha=Column(DateTime(),default=datetime.now)
	fellow_id= Column(Integer(),ForeignKey('fellow.id',onupdate="CASCADE", ondelete="CASCADE"))



	def __init__(self,name,path,hashed_name):

		self.name=name
		self.hashed_name=hashed_name
		self.path=path


	def __repr__(self):

		return(str['Fellow Documents',self.nombre,self.hashed_name,
		self.fecha,
		self.relative_path])

class EvaluationFellows(Base):

	__tablename__='evaluation_fellows'
	id=Column(Integer(),primary_key=True)
	previousInvestigationScore=Column(Integer(),nullable=False)
	previousInvestigation =Column(Text(5000),nullable=False)
	currentInvestigationScore = Column(Integer(),nullable=False)
	currentInvestigation = Column(Text(5000),nullable=False)
	purposeApplicationScore  = Column(Text(),nullable=False)
	purposeApplication = Column(Text(5000),nullable=False)
	otherTrainingCoursesScore = Column(Integer(),nullable=False)
	otherTrainingCourses = Column(Text(5000),nullable=False)
	finalReviewScore = Column(Integer(),nullable=False)
	finalReview = Column(Text(5000),nullable=False)

	## Campos para facilitar los queries y hacer mejores filtrajes
	evaluator_id=Column(Integer(),nullable=False)
	evaluator_name=Column(String(50))
	evaluator_email=Column(String(80))
	evaluated_date=Column(DateTime(),default=datetime.now)


	## llave foranea para la evaluacion de las tablas
	fellow_id= Column(Integer(),ForeignKey('fellow.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self, previousInvestigationScore,previousInvestigation,currentInvestigationScore,\
	currentInvestigation,purposeApplicationScore,purposeApplication,otherTrainingCoursesScore,\
	otherTrainingCourses,finalReviewScore,finalReview,evaluator_id="",evaluator_name="",evaluator_email=""):

		self.previousInvestigationScore=previousInvestigationScore
		self.previousInvestigation=previousInvestigation
		self.currentInvestigationScore=currentInvestigationScore
		self.currentInvestigation=currentInvestigation
		self.purposeApplicationScore=purposeApplicationScore
		self.purposeApplication=purposeApplication
		self.otherTrainingCoursesScore=otherTrainingCoursesScore
		self.otherTrainingCourses=otherTrainingCourses
		self.finalReviewScore=finalReviewScore
		self.finalReview=finalReview
		self.evaluator_id=evaluator_id
		self.evaluator_name=evaluator_name
		self.evaluator_email=evaluator_email

	def __repr__(self):

	    return(str(['evaluationFellows',

		self.previousInvestigationScore,
		self.previousInvestigation,
		self.currentInvestigationScore,
		self.currentInvestigation,
		self.purposeApplicationScore,
		self.purposeApplication,
		self.otherTrainingCoursesScore,
		self.otherTrainingCourses,
		self.finalReviewScore,
		self.finalReview,
		self.evaluator_id,
		self.evaluator_name]))


class EvaluationFellowsBackup(Base):

	__tablename__='evaluation_fellows_backup'
	id=Column(Integer(),primary_key=True)
	previousInvestigationScore=Column(Integer(),nullable=False)
	previousInvestigation =Column(Text(5000),nullable=False)
	currentInvestigationScore = Column(Integer(),nullable=False)
	currentInvestigation = Column(Text(5000),nullable=False)
	purposeApplicationScore  = Column(Text(),nullable=False)
	purposeApplication = Column(Text(5000),nullable=False)
	otherTrainingCoursesScore = Column(Integer(),nullable=False)
	otherTrainingCourses = Column(Text(5000),nullable=False)
	finalReviewScore = Column(String(10),nullable=False)
	finalReview = Column(Text(5000),nullable=False)

	## Campos para facilitar los queries y hacer mejores filtrajes
	evaluator_id=Column(Integer(),nullable=False)
	evaluator_name=Column(String(50))
	evaluator_email=Column(String(80))
	evaluated_date=Column(DateTime(),default=datetime.now)


	## llave foranea para la evaluacion de las tablas
	fellow_id= Column(Integer(),ForeignKey('fellow.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self, previousInvestigationScore="",previousInvestigation="",currentInvestigationScore="",\
	currentInvestigation="",purposeApplicationScore="",purposeApplication="",otherTrainingCoursesScore="",\
	otherTrainingCourses="",finalReviewScore="",finalReview="",evaluator_id="",evaluator_name="",evaluator_email=""):

		self.previousInvestigationScore=previousInvestigationScore
		self.previousInvestigation=previousInvestigation
		self.currentInvestigationScore=currentInvestigationScore
		self.currentInvestigation=currentInvestigation
		self.purposeApplicationScore=purposeApplicationScore
		self.purposeApplication=purposeApplication
		self.otherTrainingCoursesScore=otherTrainingCoursesScore
		self.otherTrainingCourses=otherTrainingCourses
		self.finalReviewScore=finalReviewScore
		self.finalReview=finalReview
		self.evaluator_id=evaluator_id
		self.evaluator_name=evaluator_name
		self.evaluator_email=evaluator_email

	def __repr__(self):

	    return(str(['evaluationFellows',

		self.previousInvestigationScore,
		self.previousInvestigation,
		self.currentInvestigationScore,
		self.currentInvestigation,
		self.purposeApplicationScore,
		self.purposeApplication,
		self.otherTrainingCoursesScore,
		self.otherTrainingCourses,
		self.finalReviewScore,
		self.finalReview,
		self.evaluator_id,
		self.evaluator_name]))

class FellowBackup(Base):

	__tablename__="fellowbackup"
	## Debo agregarle nombre al postulante
	id = Column(Integer(),primary_key=True, autoincrement=False)
	name= Column(String(30)) ## nombre del postulante
	priority = Column(String(2))

	fellowTitle = Column(String(40))
	destination= Column(String(50))
	generalObjective= Column(String(300))
	justification= Column(String(300))
	methodology = Column(String(300)) ## nombre de la institucion
	workingPlan = Column(String(400))
	fellow_userTokenId=Column(String(200))
	fellow_candidateEmail=Column(String(80))

	## Flags necesarias para crear la funcionalidad de la aplicación
	status_aprobado= Column(String(10),default=False)
	creation_date= Column(DateTime(),nullable=False, default=datetime.now)
	revisiones_completadas= Column(Integer(),nullable=True)
	evaluators_asignedCount=Column(Integer(),nullable=False)

	## Relacion foranea con la tabla de objetivos de cada Fellow
	fellowObjectives= relationship("FellowObjectivesBackup", cascade="save-update, delete", backref=backref('fellow'))

	## Relacion foranea con la tabla de Actividades de cada fellow
	fellowActivities= relationship("FellowActivitiesBackup", cascade="save-update, delete", backref=backref('fellow'))

	## Relacion con la tabla de documentos del postulante
	fellowDocs = relationship("FellowDocumentsBackup",cascade="save-update, delete", backref=backref('fellow'))


	def __init__(self,id=0,name="",priority=False,\
	fellowTitle="",destination="",generalObjective="",justification="",\
	methodology="",workingPlan="",status_aprobado="Pending",revisiones_completadas=False,fellow_userTokenId="",\
	fellow_candidateEmail="",evaluators_asignedCount=""):

		self.id=id
		self.name=name
		self.priority=priority
		self.fellowTitle=fellowTitle
		self.destination=destination
		self.generalObjective=generalObjective
		self.justification=justification
		self.methodology=methodology
		self.workingPlan=workingPlan
		self.status_aprobado=status_aprobado
		self.revisiones_completadas=revisiones_completadas
		self.fellow_userTokenId=fellow_userTokenId
		self.fellow_candidateEmail=fellow_candidateEmail
		self.evaluators_asignedCount=evaluators_asignedCount

	def __repr__(self):

		return(str(['fellowBackup',self.id,self.name,self.priority,\

		self.fellowTitle,
		self.destination,
		self.generalObjective,
		self.justification,
		self.methodology,
		self.workingPlan,
		self.status_aprobado,
		self.revisiones_completadas]))

class FellowObjectivesBackup(Base):

	__tablename__= 'fellowObjectivesBackup'

	id=Column(Integer(),primary_key=True)
	objective_item=Column(String(200),nullable=False)

	## Llave  foranea con el curso donde se postula esta data
	fellow_id=Column(Integer(),ForeignKey('fellowbackup.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,objective_item=""):

		self.objective_item= objective_item

	def __repr__(self):

		return(str(['fellowObjectives',self.objective_item]))

class FellowActivitiesBackup(Base):

	__tablename__= 'fellowActivitiesBackup'

	id=Column(Integer(),primary_key=True)
	activity_item=Column(String(100),nullable=False)

	## Llave  foranea con el curso donde se postula esta data.
	fellow_id=Column(Integer(),ForeignKey('fellowbackup.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)

	def __init__(self,activity_item=""):

		self.activity_item= activity_item

	def __repr__(self):

		return(str(['fellowActivities',self.activity_item]))

class FellowDocumentsBackup(Base):

	__tablename__= 'fellowDocumentsBackup'

	id= Column(Integer(),primary_key=True)
	name=Column(String(100))
	path= Column(String(100))
	hashed_name= Column(String(100))
	fecha=Column(DateTime(),default=datetime.now)
	fellow_id= Column(Integer(),ForeignKey('fellowbackup.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self,name,path,hashed_name):

		self.name=name
		self.hashed_name=hashed_name
		self.path=path


	def __repr__(self):

		return(str(['Fellow Documents',self.nombre,self.hashed_name,
		self.fecha,
		self.relative_path]))

class Notifications(Base):

	__tablename__= 'notifications'

	id= Column(Integer(),primary_key=True)
	name=Column(String(100))
	message= Column(String(150))
	date=Column(DateTime(),default=datetime.now)
	notifications_type= Column (String(150) )
	user_id= Column(Integer(),ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE"))


	def __init__(self,name,message,date,notifications_type):

		self.name=name
		self.message=message
		self.date=date
		self.notifications_type=notifications_type


	def __repr__(self):

		return(str(['Notifications',self.name,
		self.message,
		self.date,
		self.user_id,
		self.notifications_type]))


# #### Curso Backup
# class CursoBackup(Base):
#
# 	__tablename__='cursobackup'
# 	id=Column(Integer(),primary_key=True)
# 	priority=Column(Boolean())
# 	courseTitle=Column(String(80))
# 	hostname=Column(String(80))
# 	destination=Column(String(80))
# 	hostAddress=Column(String(80))
# 	coordName=Column(String(80))
# 	coordTitle=Column(String(80))
# 	coordAffiliation=Column(String(80))
# 	commDate=Column(DateTime(),nullable=False)
# 	termDate=Column(DateTime(),nullable=False)
# 	courseDescription=Column(String(2000))
# 	organizationTrainingDescription=Column(String(2000))
# 	## agregar expectedOutput
# 	courseTrainees=Column(String(2000))
# 	#course_candidateEmail(String(80),nullable=False)
#
# 	## Flags para conocer el status del curso
#
# 	status_aprobado=Column(Boolean(),default=False)
# 	status_revisado=Column(Boolean(),default=False) ## En evaluacion
# 	revisiones_completadas=Column(Integer(),default=0)
# 	user_candidateId=Column(String(200),nullable=False)
# 	user_candidateEmail=Column(String(100),nullable=False)
#
#
# 	## Id del usuario que postulo el curso
# 	postulanteCurso_id= Column(Integer(),ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)
#
# 	## Relacion con la tabla de documentos del curso
# 	cursoDocs = relationship("DocumentosCursosBackup", cascade="save-update,delete",backref=backref('curso'))
#
# 	## Relacion con la tabla de objetivos del curso
# 	courseObjectives=relationship("CourseObjectivesBackup", cascade="save-update, delete", backref=backref('curso'))
#
# 	## Relacion con la tabla de colaboradores de los cursos
# 	courseCollaborators=relationship("CourseCollaboratorsBackup",cascade="save-update,delete", backref=backref('curso'))
#
# 	## Relaciona con la tabla de budget Items
# 	courseBudgetItems=relationship("CourseBudgetsItemsBackup", cascade="save-update, delete", backref=backref('curso'))
#
# 	def __init__(self, courseTitle="", hostName="", hostAddress="", coordName="", coordTitle="",\
# 	 	coordAffiliation="", commDate="", termDate="", courseDescription="", organizationTrainingDescription="",\
# 		courseTrainees="",priority=False,destination="",user_candidateId="",user_candidateEmail=""):
#
# 		self.priority=priority
# 		self.courseTitle=courseTitle
# 		self.hostName=hostName
# 		self.hostAddress=hostAddress
# 		self.coordName=coordName
# 		self.coordTitle=coordTitle
# 		self.coordAffiliation=coordAffiliation
# 		self.commDate=commDate
# 		self.termDate=termDate
# 		self.courseDescription=courseDescription
# 		self.organizationTrainingDescription=organizationTrainingDescription
# 		self.courseTrainees=courseTrainees
# 		self.user_candidateId=user_candidateId
# 		self.user_candidateEmail=user_candidateEmail
#
#
#
# 	def __repr__(self):
#
# 		return(str(['cursos',\
#
# 		self.priority,
# 		self.courseTitle,
# 		self.hostname,
# 		self.hostAddress,
# 		self.coordName,
# 		self.coordTitle,
# 		self.coordAffiliation,
# 		self.commDate,
# 		self.termDate,
# 		self.courseDescription,
# 		self.organizationTrainingDescription,
# 		self.user_candidateId,
# 		self.user_candidateEmail,
# 		self.courseTrainees]))
#
#
# class CourseObjectivesBackup(Base):
#
# 	__tablename__='courseObjectivesBackup'
# 	id=Column(Integer(),primary_key=True)
# 	objective_item=Column(String(200),nullable=False)
#
# 	## Llave  foranea con el curso donde se postula esta data
# 	curso_id=Column(Integer(),ForeignKey('cursobackup.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)
#
# 	def __init__(self,objective_item=""):
#
# 		self.objective_item= objective_item
#
# 	def __repr__(self):
#
# 		return(str(['coursesObjectives',self.objective_item]))
#
#
# class CourseBudgetsItemsBackup(Base):
#
# 	__tablename__='courseBudgetItemsBackup'
# 	id=Column(Integer(),primary_key=True)
# 	budget_desc=Column(String(120))
# 	budget_value=Column(String(10))
#
# 	## Llave  foranea con el curso donde se postula esta data
# 	curso_id=Column(Integer(),ForeignKey('cursobackup.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)
#
# 	def __init__(self,budget_desc="",budget_value=""):
#
# 		self.budget_desc=budget_desc
# 		self.budget_value=budget_value
#
# 	def __repr__(self):
#
# 		return(str(['coursesBudgetItems',self.budget_desc,self.budget_value]))
#
# class CourseCollaboratorsBackup(Base):
#
# 	__tablename__='courseCollaboratorsBackup'
# 	id=Column(Integer(),primary_key=True)
# 	coll_name=Column(String(20))
# 	coll_position=Column(String(20))
# 	coll_institution=Column(String(30))
# 	coll_phone=Column(String(20))
# 	coll_email=Column(String(70))
# 	coll_area=Column(String(15))
# 	coll_cv=Column(String(100))
#
# 	## Llave  foranea con el curso donde se postula esta data
# 	curso_id=Column(Integer(),ForeignKey('cursobackup.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)
#
# 	def __init__(self,coll_name="",coll_position="",coll_institution="",coll_phone="",\
# 		coll_email="",coll_area="",coll_cv="Probando path"):
#
# 		self.coll_name=coll_name
# 		self.coll_position=coll_position
# 		self.coll_phone=coll_phone
# 		self.coll_institution=coll_institution
#
# 		self.coll_email=coll_email
# 		self.coll_area=coll_area
# 		self.coll_cv=coll_cv
#
# 	def __repr__(self):
#
# 		return(str(['coursescollaborators',self.coll_name,\
# 		self.coll_position,
# 		self.coll_institution,
# 		self.coll_phone,
#
# 		self.coll_email,
# 		self.coll_area,
# 		self.coll_cv]))
#
# class DocumentosCursosBackup(Base):
#
# 	__tablename__= 'documentos_cursos_backup'
#
# 	id= Column(Integer(),primary_key=True)
# 	name = Column(String(80),nullable=True)
# 	path= Column(String(100))
# 	hashed_name= Column(String(100))
# 	fecha=Column(DateTime(),default=datetime.now)
# 	curso_id= Column(Integer(),ForeignKey('cursobackup.id',onupdate="CASCADE", ondelete="CASCADE"))
#
# 	def __init__(self,name,path,hashed_name):
#
# 		self.name=name
# 		self.path=path
# 		self.hashed_name=hashed_name
#
#
# 	def __repr__(self):
#
# 		return(str['Documentos Cursos',self.nombre,self.hashed_name,
# 		self.fecha,
# 		self.relative_path])

class LogEvaluadores(Base):

	__tablename__='log_evaluadores'
	id=Column(Integer(),primary_key=True)
	evaluated_date=Column(DateTime(),default=datetime.now)
	evaluator_name=Column(String(50),nullable=False)
	evaluator_email=Column(String(50),nullable=False)
	postulation_type=Column(String(50),nullable=False)
	fellow_evaluated_id=Column(Integer(),nullable=False)
	fellow_evaluated_title=Column(String(80),nullable=False)
	fellow_candidateEmail=Column(String(80),nullable=False)

	## llave foranea con la tabla de cursos
	user_evaluator_id= Column(Integer(),ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE"),nullable=False)


	def __init__(self, evaluator_name,evaluator_email, postulation_type, fellow_evaluated_id,\
	fellow_evaluated_title,fellow_candidateEmail):

		self.evaluator_name=evaluator_name
		self.evaluator_email=evaluator_email
		self.postulation_type=postulation_type
		self.fellow_evaluated_id=fellow_evaluated_id
		self.fellow_evaluated_title=fellow_evaluated_title
		self.fellow_candidateEmail=fellow_candidateEmail

	## Representacion de la clase logEvaluadores
	def __repr__(self):

	    return(str(['log_evaluadores',

		self.evaluator_name,
		self.evaluator_email,
		self.postulation_type,
		self.fellow_evaluated_id,
		self.fellow_evaluated_title,
		self.fellow_candidateEmail]))

class LogApplications(Base):

	__tablename__='log_applications'
	id=Column(Integer(),primary_key=True)
	application_date=Column(DateTime(),default=datetime.now)
	application_name=Column(String(50),nullable=False)
	application_id=Column(Integer(),nullable=False)
	application_type=Column(String(50),nullable=False)
	application_title=Column(String(80),nullable=False)
	application_candidateMail= Column(String(80),nullable=False)
	application_candidateId=Column(Integer(),nullable=False)


	def __init__(self,application_name,application_id,application_type, application_title,\
	application_candidateMail,application_candidateId):

		self.application_name=application_name
		self.application_id=application_id
		self.application_type=application_type
		self.application_title=application_title
		self.application_candidateMail=application_candidateMail
		self.application_candidateId=application_candidateId

	## Representacion de la clase logEvaluadores
	def __repr__(self):

	    return(str(['log_applications',

		self.application_name,
		self.application_id,
		self.application_type,
		self.application_title,
		self.application_candidateMail,
		self.application_candidateId]))


class SaveFellow(Base):

    __tablename__='save_fellow'
    id=Column(Integer(),primary_key=True)
    data=Column(PickleType)

    user_id= Column(Integer(),ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE"))

    def __init__(self,data=""):

    	self.data=data

    def __repr__(self):

        return(str(['blob',

    	self.data]))

class SaveCourse(Base):

	__tablename__='save_course'
	id=Column(Integer(),primary_key=True)
	data=Column(PickleType)

	user_id= Column(Integer(),ForeignKey('users.id',onupdate="CASCADE", ondelete="CASCADE"))

	def __init__(self,data=""):

		self.data=data

	def __repr__(self):

	    return(str(['blob',

		self.data]))
