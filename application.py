from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.cdn import CDN

db = MongoEngine()
cdn = CDN()

def create_app(**config_overrides):
    app = Flask(__name__)

    # Load config
    app.config.from_pyfile('settings.py')

    # apply overrides for tests
    app.config.update(config_overrides)

    # setup db
    db.init_app(app)

    # setup CDN
    cdn.init_app(app)

    # import blueprints
    from user.views import user_app
    from relationship.views import relationship_app
    from feed.views import feed_app
    from home.views import home_app
    from course.views import course_app

    # register blueprints
    app.register_blueprint(user_app)
    app.register_blueprint(relationship_app)
    app.register_blueprint(feed_app)
    app.register_blueprint(home_app)
    app.register_blueprint(course_app)

    return app
