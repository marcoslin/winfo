'''
Created on 27 June 2013

@author: Marcos Lin

User Info Provider
'''

from flask import Blueprint, Response, request

from models.user import UserDao

def blueprint():
    bp = Blueprint('user_service', __name__)
    user = UserDao()
    
    #
    # User Section
    #
    @bp.route("/", methods=['GET'])
    def user_query():
        return Response(user.query(), mimetype="application/json") 
                
    @bp.route("/<string:user_id>", methods=['GET', 'PUT'])
    def user_get_put(user_id):
        if request.method == "GET":
            res = user.get(user_id)
        elif request.method == "PUT":
            res = user.update(user_id, request.json)
        
        if res:
            return Response(res,mimetype="application/json")
        else:
            return "NOT FOUND.", 404

    @bp.route("/add", methods=['POST'])
    def user_add():
        json_data = request.json
        if json_data:
            # Need to read the key and data
            user_name=json_data["user_name"]
            
            # Make sure user_name does not currently exists
            if user.check_user_name_exists(user_name):
                return "Error: Username '%s' taken." % user_name, 500
            
            res = user.add(json_data)
            if res:
                return Response(res,mimetype="application/json")
            else:
                return "Internal Server Error.", 500

    @bp.route("/<string:user_id>", methods=['DELETE'])
    def json_contact_update(user_id):
        user.delete(user_id)
        return "DELETED.", 200

    return bp
    
