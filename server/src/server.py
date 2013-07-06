import lib  # @UnresolvedImport
from flask import Flask, redirect

from app.core import ConfigurationStore
from routes import auth_service, user_service
from auth import Authenticator


auth = Authenticator()
app = Flask(__name__)
# configuration: no need to keep the reference as it is Singleton
with ConfigurationStore(logger=app.logger) as config:
    # Set the config file
    app.config.from_object(config)


@app.route("/")
def redirect_to_app():
    return redirect("/app/")

app.register_blueprint(auth_service.blueprint(auth), url_prefix="/auth")
app.register_blueprint(user_service.blueprint(), url_prefix="/d/user")

