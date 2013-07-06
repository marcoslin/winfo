
from flask import Response
from models.user import User

class Authenticator(object):
    def login(self, request):
        json_data = request.json
        if json_data:
            try:
                user_name = json_data["user_name"]
                password = json_data["password"]
            except (TypeError, KeyError):
                #self.logger.debug("Failed to read user from request.")
                print "Failed to read user from request."
                return self.unauthorized()
        
            user = User.get_by_user_name(user_name)
            if user:
                if password == user.secure_passwd_hash:
                    return "Login Successful", 200
        
        return self.unauthorized("Login Failed.")
            

    def logout(self, request):
        # Do nothing
        return "Logged out from server", 200

    def challenge(self, request):
        # No challenge implemented.
        return "Not Found.", 404

    def unauthorized(self, message=None):
        '''Returns an 401 Unauthorized HTTP Response'''
        if message is None:
            message = "Unauthorized"
        resp = Response(message, status=401)
        return resp