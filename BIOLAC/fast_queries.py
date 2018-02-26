from models import *
from database import dbSession, session_manager
import datetime

# from itsdangerous import URLSafeSerializer
# ts=URLSafeSerializer("key")

with session_manager() as session:
    # data=session.query(User,Fellow).join(Fellow, Fellow.id==User.id).filter(Fellow.id==2).first()
    # #data=session.query(User,Fellow).join(Fellow, User.id==Fellow.id).all()
    # #data=session.query(User,Fellow).join(Fellow, 2==Fellow.id).first()
    #
    # completed=session.query(evaluandocourses_table).filter_by(evaluation_status=True,user_id=3).all()
    # keys=[ c.curso_id for c in completed]
    #
    # ## Hago un query de todos los cursos que no he evaluado
    # data=session.query(Curso).filter(Curso.id.in_(keys)).all()
    # # print(data[0].name)
    # score=session.query(EvaluationCourses.overallQualification).filter(EvaluationCourses.curso_id.in_(keys),\
    # EvaluationCourses.evaluator_id==3).all()
    # print(score[0][0])

# x=ts.dumps("1")
# print(type(x))
