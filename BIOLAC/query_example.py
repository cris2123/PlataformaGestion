app.route("/Evaluate/Course")
def evaluate_form_course():

    # try:
    #     user_id = serializer.loads(token, salt="passing_id")
    #     user_id=int(user_id)
    #
    # except Exception as e:
    #
    #     return("Ocurrio un error" + str(e) )

    with session_manager() as session:

        data=session.query(Fellow,FellowObjectives,FellowActivities)\
        .join(FellowObjectives)\
        .join(FellowActivities)\
        .filter(Fellow.id==2).all() ## aqui usaremos current_user.id
        return(str(data))


    form = MiniForm()


    Query de pinga para resolver el problema de todas las activities y demas
