'''
Created on 25 May 2013

@author: Marcos Lin

JSON Data Provider

ToDo: Figure around Angular's $resource behaviour when optinal parameter is not called.  E.g.:
query calls: "/contact/"
put calls:   "/contact"

'''

import json
from flask import Blueprint, Response, request

from models.intro import ContactDao

def blueprint(idgen):
    bp = Blueprint('json', __name__)
    contact = ContactDao()
    
    # ========================================
    # Initialize with some data if needed
    ContactDao.initialize()
        
    @bp.route("/id64")
    def json_id64():
        return "ID64: %d" % idgen.id64("intro.id64")

    @bp.route("/headers", methods=['GET'])
    def json_headers():
        headers = []
        for key, val in request.headers.iteritems():
            headers.append({ "name": key, "content": val })
        return Response(json.dumps(headers),mimetype="application/json")

    @bp.route("/contact/", methods=['GET'])
    def json_contact_all():
        return Response(contact.query(), mimetype="application/json") 

    @bp.route("/contact/<string:contact_id>", methods=['GET', 'PUT'])
    def json_contact_get(contact_id):
        if request.method == "GET":
            res = contact.get(contact_id)
        elif request.method == "PUT":
            res = contact.update(contact_id, request.json)
        
        if res:
            return Response(res,mimetype="application/json")
        else:
            return "NOT FOUND.", 404

    @bp.route("/contact", methods=['POST'])
    def json_contact_add():
        res = contact.add(request.json)
        if res:
            return Response(res,mimetype="application/json")
        else:
            return "Internal Server Error.", 500

    @bp.route("/contact/<string:contact_id>", methods=['DELETE'])
    def json_contact_update(contact_id):
        contact.delete(contact_id)
        return "DELETED.", 200

    return bp
    
