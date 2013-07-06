#!/usr/bin/env python

import sys
sys.path.append("../python/")
import utils

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from pprint_ndb import display_entity, display_all

class User(ndb.Model):
     name = ndb.StringProperty()

class Friendship (ndb.Model):
    friends = ndb.KeyProperty(kind=User, repeated=True)
    
    @classmethod
    def get_friends_keys(cls, user_key):
        for entry in cls.query(ancestor=user_key):
            return entry.friends

userA = User(name="User A")
userA_key = userA.put()

userB = User(name="User B")
userB_key = userB.put()

userC = User(name="User C")
userC_key = userC.put()

# Set userB as friend of userA
f = Friendship(friends=[userB_key, userC_key], parent=userA_key)
f.put()

# To retrieve all friends
for user in ndb.get_multi(Friendship.get_friends_keys(userA_key)):
    print "user: %s" % user.name
