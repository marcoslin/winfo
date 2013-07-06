#!/usr/bin/env python

import sys
sys.path.append("../python/")
import utils

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from pprint_ndb import display_entity, display_all

class Dummy(ndb.Model):
     anything = ndb.StringProperty()

class User(ndb.Model):
     name = ndb.StringProperty()
     friends = ndb.KeyProperty(kind="User", repeated=True)

userB = User(name="User B")
userB_key = userB.put()

userC = User(name="User C")
userC_key = userC.put()

dummy = Dummy(anything="Hello")
dummy_key = dummy.put()

userA = User(name="User A", friends=[userB_key, userC_key])
userA_key = userA.put()


# To retrieve all friends
for user in ndb.get_multi(userA.friends):
    print "user: %s" % user.name
