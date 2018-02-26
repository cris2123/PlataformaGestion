from models import *
from application import serializer
from database import dbSession, session_manager
import datetime

#################### Agregando los permisos por default ######################

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
    "0412-7256957","0212-9858996",profile_picture="/data",token=token_id)
    role_q.users.append(user)
    session.add(user)


with session_manager() as session:
    role_q3=session.query(Role).get(3)
    token_id2=serializer.dumps(str(2),salt="passing_id")
    user3=User("cristhian6bravo@gmail.com","Hola12#","Cristhian","Perez",datetime.datetime.now(),"Venezolano","Hombre",\
    "single","venezuela","Caracas",1061,"El cafetal","USB",\
    "algo","algo","bachiller","bachiller","usb",\
    "0412-7256957","0212-9858996",profile_picture="/data",token=token_id2)
    role_q3.users.append(user3)
    session.add(user3)

with session_manager() as session:
    role_q4=session.query(Role).get(2)
    token_id4=serializer.dumps(str(3),salt="passing_id")
    user4=User("cristhian7bravo@gmail.com","Hola12#","Carlos","Perez",datetime.datetime.now(),"Venezolano","Hombre",\
    "single","venezuela","Caracas",1061,"El cafetal","USB",\
    "algo","algo","bachiller","bachiller","usb",\
    "0412-7256957","0212-9858996",profile_picture="/data",token=token_id4)
    role_q4.users.append(user4)
    session.add(user4)

with session_manager() as session:
    role_q7=session.query(Role).get(1)
    token_id7=serializer.dumps(str(4),salt="passing_id")
    user7=User("cristhian8bravo@gmail.com","Hola12#","Jaime","Bravo",datetime.datetime.now(),"Venezolano","Hombre",\
    "single","venezuela","Caracas",1061,"El cafetal","USB",\
    "algo","algo","bachiller","bachiller","usb",\
    "0412-7256957","0212-9858996",profile_picture="/data",token=token_id7)
    role_q7.users.append(user7)
    session.add(user7)

with session_manager() as session:
    role_q8=session.query(Role).get(1)
    token_id8=serializer.dumps(str(5),salt="passing_id")
    user8=User("cristhian9bravo@gmail.com","Hola12#","Andrea","Bravo",datetime.datetime.now(),"Venezolano","Hombre",\
    "single","venezuela","Caracas",1061,"El cafetal","USB",\
    "algo","algo","bachiller","bachiller","usb",\
    "0412-7256957","0212-9858996",profile_picture="/data",token=token_id8)
    role_q8.users.append(user8)
    session.add(user8)





with session_manager() as session:
    user=session.query(User).filter(User.email=="cristhian3bravo@gmail.com").update({User.active:True})
    user2=session.query(User).filter(User.email=="cristhian6bravo@gmail.com").update({User.active:True})
    user4=session.query(User).filter(User.email=="cristhian7bravo@gmail.com").update({User.active:True})
    user5=session.query(User).filter(User.email=="cristhian8bravo@gmail.com").update({User.active:True})
    user6=session.query(User).filter(User.email=="cristhian9bravo@gmail.com").update({User.active:True})


#
# ## Probando la tabla cursos con sqlalchemy
# ## Ingresar cursos funciona perfecto
#
# user1_q=session.query(User).first()
#
# curso1=Curso('Curso1','curso tecnico1')
# curso2=Curso('Curso2', 'Curso tecnico 2')
#
# user1_q.curso.append(curso1)
# user1_q.curso.append(curso2)
#
# session.add(curso1)
# session.add(curso2)
# session.flush()
# session.commit()
#
# ## Probando queries many-to-many ## Funciona a la perfeccion ###
#
# roles=session.query(Role).join('permisos').filter_by(id=4)
#
# for r in roles:
#
# 	print(r)
