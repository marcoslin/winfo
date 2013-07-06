'''
Created on 27 June 2013

@author: Marcos Lin

User Info Provider
'''

from flask import Blueprint, Response, request

from models import UnAuthorizedException
from models.user import UserDao
from models.profile import SharableProfileDao

def blueprint():
    bp = Blueprint('profile_service', __name__)
    user = UserDao()
    profile = SharableProfileDao()
    
    #
    # Info Section
    #
    def _check_login_user(user_name):
        '''Need to ensure that user_name param matches the logon user'''
        # Place holder for now
        pass
    
    @bp.route("/info/<string:user_name>", methods=['GET'])
    def user_info_get(user_name):
        '''Return full user contact info'''
        _check_login_user(user_name)
        res = user.get_user_dict(user_name)

        if res:
            return Response(res,mimetype="application/json")
        else:
            return "NOT FOUND.", 404

    @bp.route("/info/<string:user_name>", methods=['PUT'])
    def user_info_save(user_name):
        '''Save the full user info'''
        _check_login_user(user_name)
        json_body = request.json
        print "user_info: %s" % json_body
        if json_body:
            user.save_user_dict(user_name, json_body)
            res = user.get_user_dict(user_name)
            return Response(res,mimetype="application/json")
        return "Ok", 200

    #
    # Shared Profile Section
    #
    @bp.route("/shared/<string:user_name>/profile/", methods=['GET'])
    def json_profile_all(user_name):
        '''Return a list of provider_name and provider_id'''
        _check_login_user(user_name)
        return Response(profile.query(user_name), mimetype="application/json") 

    @bp.route("/shared/<string:user_name>/profile/<string:profile_id>", methods=['GET', 'PUT'])
    def json_profile_get_put(user_name, profile_id):
        _check_login_user(user_name)
        if request.method == "GET":
            try:
                res = profile.get(user_name, profile_id)
            except UnAuthorizedException as e:
                # Return a not found 404 code so that no login prompted is triggered
                print "Error UnAuthorizedException"
                return e.message, 404
        elif request.method == "PUT":
            try:
                res = profile.update(user_name, profile_id, request.json)
            except UnAuthorizedException as e:
                # Return a not found 404 code so that no login prompted is triggered
                return e.message, 404
        
        if res:
            return Response(res,mimetype="application/json")
        else:
            return "NOT FOUND.", 404

    @bp.route("/shared/<string:user_name>/profile", methods=['POST'])
    def json_profile_add(user_name):
        _check_login_user(user_name)
        res = profile.add(user_name, request.json)
        if res:
            return Response(res,mimetype="application/json")
        else:
            return "Internal Server Error.", 500

    @bp.route("/shared/<string:user_name>/profile/<string:profile_id>", methods=['DELETE'])
    def json_profile_delete(user_name, profile_id):
        _check_login_user(user_name)
        profile.delete(user_name, profile_id)
        return "DELETED.", 200
    
    #
    # Test
    #
    @bp.route("/shared/init/<string:user_name>", methods=['GET'])
    def json_profile_init(user_name):
        jdata = profile._convert_to_json(profile.init(user_name))
        return Response(jdata, mimetype="application/json") 
    
    return bp
    
