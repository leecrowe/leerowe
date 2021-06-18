from os import getenv
from flask import Flask, render_template, request
from .twitter import add_or_update_user, update_all_users
from .predict import predict_user
from .models import DB, User, Tweet


def create_app():

    # initilizes our application
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = getenv['DATABASE_URI']
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    DB.init_app(app)

    @app.route("/")
    def root():
        users = User.query.all()
        return render_template("base.html", title='Home', users=users)


    @app.route("/compare", methods=["POST"])
    def compare():
        user0, user1 = sorted(
            [request.values["user0"], request.values["user1"]])

        if user0 == user1:
            message = "You can't compare users to themselves!"
        else:
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])

            message = "'{}' is more likely to be said by {} than {}".format(
                request.values["tweet_text"],
                user1 if prediction else user0,
                user0 if prediction else user1
            )

        return render_template("prediction.html", title="prediction", message=message)


    @app.route("/user", methods=["POST"])
    @app.route("/user/<name>", methods=["GET"])
    def user(name=None, message=''):
        name = name or request.values["user_name"]
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = "User {} was succesfully added!".format(name)

            tweets = User.query.filter(User.name == name).one().tweets

        except Exception as e:
            message = "Error handling {}: {}".format(name, e)

            tweets = []

        return render_template("user.html", title=name,
                               tweets=tweets, message=message)


    @app.route("/reset")
    def reset():
        DB.drop_all()
        DB.create_all()
        users = User.query.all()
        return render_template("base.html", title='Home', users=users)




    return app

'''
    @app.route('/update')
    def update():
        update_all_users()
        users = User.query.all()
        return render_template('base.html', title='Updated all users!', users=users)
'''


