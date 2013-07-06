#!/usr/bin/env python


import sys
sys.path.append("../python/")
import utils

from google.appengine.ext import ndb
from pprint_ndb import display_entity, display_all

#
# DEFINE MODELS
#
class Address(ndb.Model):
	type = ndb.StringProperty()
	line = ndb.StringProperty()
	city = ndb.StringProperty()
	country = ndb.StringProperty()
	
class Email(ndb.Model):
	type = ndb.StringProperty()
	email = ndb.StringProperty()
	
class User(ndb.Model):
	user_id = ndb.KeyProperty(kind="User")
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	
	addresses = ndb.StructuredProperty(Address, repeated=True)
	emails = ndb.StructuredProperty(Email, repeated=True)


#
# Model Instance.  Nested Model creation
#
entry01 = User(
	user_id = ndb.Key("User", 10),
	first_name = "Marcos",
	last_name = "Lin",
	
	addresses = [
		Address(type="work", city="London", country="UK"),
		Address(type="home", city="Rome", country="Italy")
	],
	
	emails = [
		Email(type="work", email="marcos.work@example.com"),
		Email(type="home", email="marcos.home@example.com")
	]
)
entry01.put()
display_entity(entry01)

#
# Create nested model from dict
#
data_entry02 = {
	'id': 10,
	'first_name': 'Flavia',
	'last_name': 'Lin',
	'user_id': ndb.Key('User', 10),
	'addresses': [	{ 'city': u'Sao Paulo',
	                  'country': u'Brazil',
	                  'line': None,
	                  'type': u'work'},
					{ 'city': u'Rome',
					  'country': u'Italy',
					  'line': None,
					  'type': u'home'} ],
	'emails': [ { 'email': u'flavia.work@example.com', 'type': u'work'},
				{ 'email': u'flavia.home@example.com', 'type': u'home'}],
}

entry02 = User(**data_entry02)
entry02.put()
display_entity(entry02)

#
# Retrieve and update
#
entry02a = User.get_by_id(10)
entry02a.emails.append( Email(type="home", email="flavia.home2@example.com") )
entry02a.put()

# Note that sub record does not have a key
email02 = entry02a.emails[0]
print "Email Key: %s" % email02.key

# ALL
display_all(User)
