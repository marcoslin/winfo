#!/usr/bin/env python


import sys
sys.path.append("../python/")
import utils

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from pprint_ndb import display_entity, display_all

class TestContact(ndb.Model):
    name = ndb.StringProperty()
    city = ndb.StringProperty()


pITA = ndb.Key("country", "ITA")
a = TestContact(name="A", city="Rome", parent=pITA)
a.put()
display_entity(a)

b = TestContact(name="B", city="London", parent=a.key)
b.put()
display_entity(b)

c = TestContact(name="C", city="New York", parent=b.key)
c.put()
display_entity(c)

print "# Parent key: %s" % c.key.parent().id()

print "\n# =========================="
print "# Testing query with projection"
for entry in TestContact.query().fetch(projection=[TestContact.name]):
    display_entity(entry)


print "\n# =========================="
print "# Testing query by ID with parent"

d = TestContact(id=54321, name="Mariana", parent=pITA)
d.put()
display_entity(d)
print "key: ", d.key

dkey = ndb.Key(TestContact, 54321, parent=pITA)
x = dkey.get()
#x = TestContact.get_by_id(54321)

display_entity(x)

sys.exit()


print "# =========================="

class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty(required = True)
    providers = ndb.KeyProperty(repeated=True)
    
class AuthProvider(polymodel.PolyModel):
    user = ndb.KeyProperty(kind=User)

class FacebookProvider(AuthProvider):
    fb_username = ndb.StringProperty()

class TwitterProvider(AuthProvider):
    tw_username = ndb.StringProperty()

auser = User(id="auser", name="A User", email="auser@example.com")
auser_key = auser.put()

fbuser = FacebookProvider(id=123, fb_username="auser.1", user=auser_key)
fbuser_key = fbuser.put()

twuser = TwitterProvider(id=123, tw_username="auser.tw", user=auser_key)
twuser_key = twuser.put()

if fbuser_key == twuser_key:
    print "Equal"


#
# Notice how fbuser is overwritten
#
print "#########################"
print "# Displaying AuthProvider"
display_entity(fbuser)
display_entity(twuser)

print "Auth: %s" % FacebookProvider.get_by_id(123)
print "User: %s" % User.get_by_id("auser")

fbkey = ndb.Key("ProviderId", 123, "ProviderName", "fb")

buser = User(id="buser", name="B user", email="buser@example.com")
buser.providers = [
    ndb.Key("ProviderId", 123, "ProviderName", "fb"),
    ndb.Key("ProviderId", 124, "ProviderName", "tw")
]
buser.put()
display_entity(buser)

print "#########################"
print "# AuthProvider"
authusers = AuthProvider.query().filter(AuthProvider.user == auser_key)
for y in authusers:
    print y
print "#========================"

print "FB: ", fbkey.get()

for x in User.query(User.providers==fbkey):
    print x