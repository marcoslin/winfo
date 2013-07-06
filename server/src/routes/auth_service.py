'''
Created on 12 Jun 2013

@author: Marcos Lin

Authentication Service Provider
'''

from flask import Blueprint, request

def blueprint(auth):
    bp = Blueprint('auth', __name__)
    
    @bp.route("/")
    def index():
        return "<!DOCTYPE html><H1>This is the AUTH</H1>"
    
    @bp.route("/login", methods=['POST'])
    def login():
        return auth.login(request)
    
    @bp.route("/logout")
    def logout():
        return auth.logout(request)
    
    @bp.route("/challenge", methods=['GET', 'POST'])
    def challenge():
        return auth.challenge(request)


    return bp

