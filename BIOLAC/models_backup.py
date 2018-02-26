class Curso(Base):

	__tablename__='curso'
	id=Column(Integer(),primary_key=True)
	priority1=Column(Boolean())
	priority2=Column(Boolean())
	priority3=Column(Boolean())
	courseTitle=Column(String(80))
	hostname=Column(String(80))
	hostAddress=Column(String(80))
	coordName=Column(String(80))
	coordTitle=Column(String(80))
	coordAffiliation=Column(String(80))
	commDate=Column(DateTime(),nullable=False)
	termDate=Column(DateTime(),nullable=False)
	courseDescription=Column(String(2000))
	organizationTrainingDescription=Column(String(2000))
	courseTrainees=Column(String(2000))

	## Flags para conocer el status del curso

	status_aprobado=Column(Boolean(),default=False)
	status_revisado=Column(Boolean(),default=False) ## En evaluacion

	## Id del usuario que postulo el curso
	postulanteCurso_id= Column(Integer(),ForeignKey('users.id'),nullable=False)

	## Relacion con la tabla de documentos del curso
	cursoDocs = relationship("DocumentosCursos", cascade="delete",backref=backref('curso'))

	## Relacion con la tabla de objetivos del curso
	courseObjectives=relationship("CourseObjectives", cascade="delete", backref=backref('curso'))

	## Relacion con la tabla de colaboradores de los cursos
	courseCollaborators=relationship("CourseCollaborators",cascade="delete", backref=backref('curso'))

	# Para debugging agregar una manera de setear los flags en la instanciacion
	# Puedo ponerlo por default y cuando lo instancio ponerlo True
	def __init__(self, courseTitle, hostname, hostAddress, coordName, coordTitle,\
	 	coordAffiliation, commDate, termDate, courseDescription, organizationTrainingDescription,\
		courseTrainees,priority1=False,priority2=False, priority3=False):

		self.priority1=priority1
		self.priority2=priority2
		self.priority3=priority3
		self.courseTitle=courseTitle
		self.hostname=hostname
		self.hostAddress=hostAddress
		self.coordName=coordName
		self.coordTitle=coordTitle
		self.coordAffiliation=coordAffiliation
		self.commDate=commDate
		self.termDate=termDate
		self.courseDescription=courseDescription
		self.organizationTrainingDescription=organizationTrainingDescription
		self.courseTrainees=courseTrainees



	def __repr__(self):

		return(str(['cursos',\

		self.priority1,
		self.priority2,
		self.priority3,
		self.courseTitle,
		self.hostname,
		self.hostAddress,
		self.coordName,
		self.coordTitle,
		self.coordAffiliation,
		self.commDate,
		self.termDate,
		self.courseDescription,
		self.organizationTrainingDescription,
		self.courseTrainees]))

class CourseObjectives(Base):

	__tablename__='courseObjectives'
	id=Column(Integer(),primary_key=True)
	objective_item=Column(String(200),nullable=False)

	## Llave  foranea con el curso donde se postula esta data
	curso_id=Column(Integer(),ForeignKey('curso.id'),nullable=False)

	def __init__(self,objective_item):

		self.objective_item= objective_item

	def __repr__(self):

		return(str(['coursesObjectives',self.objective_item]))

class CourseCollaborators(Base):

	__tablename__='courseCollaborators'
	id=Column(Integer(),primary_key=True)
	coll_name=Column(String(20))
	coll_position=Column(String(20))
	coll_institution=Column(String(30))
	coll_phone=Column(String(20))
	coll_fax=Column(String(26))
	coll_email=Column(String(70))
	coll_area=Column(String(15))
	coll_cv=Column(String(30))

	## Llave  foranea con el curso donde se postula esta data
	curso_id=Column(Integer(),ForeignKey('curso.id'),nullable=False)

	def __init__(self,coll_name,coll_position,coll_institution,coll_phone,coll_fax,\
		coll_email,coll_area,coll_cv="Probando path"):

		self.coll_name=coll_name
		self.coll_position=coll_position
		self.coll_institution=coll_institution
		self.coll_phone=coll_phone
		self.coll_fax=coll_fax
		self.coll_email=coll_email
		self.coll_area=coll_area
		self.coll_cv=coll_cv

	def __repr__(self):

		return(str(['coursescollaborators',self.coll_name,\
		self.coll_position,
		self.coll_institution,
		self.coll_phone,
		self.coll_fax,
		self.coll_email,
		self.coll_area,
		self.coll_cv]))

class CourseBudgetsItems(Base):

	__tablename__='courseBudgetItems'
	id=Column(Integer(),primary_key=True)
	budget_desc=Column(String(120))
	budget_value=Column(String(10))

	## Llave  foranea con el curso donde se postula esta data
	curso_id=Column(Integer(),ForeignKey('curso.id'),nullable=False)

	def __init__(self,budget_desc,budget_value):

		self.budget_desc=budget_desc
		self.budget_value=budget_value

	def __repr__(self):

		return(str(['coursesBudgetItems',self.budget_desc,self.budget_value]))
