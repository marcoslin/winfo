#!/usr/bin/env python


import sys
sys.path.append("../python/")
import utils

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel
from pprint_ndb import pprint_dict, display_entity, display_all

#
# DEFINE MODELS BASE CLASSES
#
class NdbUtilMixIn(object):
	'''
	This MixIn allow updating of entities using key
	'''
	@classmethod
	def update_model(self, model, **kwargs):
		for key in kwargs:
			setattr(model,key,kwargs[key])
		model.put()
	
	@classmethod
	def query_by_urlsafe(cls, urlsafe_id):
		entry = ndb.Key(urlsafe=urlsafe_id).get()
		if entry:
			if isinstance(entry, cls):
				return entry
			else:
				raise ValueError("urlsafe_id passed is a '%s' but current class is '%s'" % (entry.__class__.__name__, cls.__name__))

	@classmethod
	def get_first(cls, *args):
		'''Return first record'''
		for entry in cls.query(*args):
			return entry

	def update(self, **kwargs):
		'''Instance method used to update a Model'''
		self.update_model(self, **kwargs)
		


class ContactDetailType(polymodel.PolyModel, NdbUtilMixIn):
	'''
	The base class for all contact attribute with type
	'''
	type = ndb.StringProperty(indexed=True, required=True)
	
	@classmethod
	def set(cls, parent_key, type, **kwargs):
		'''Update or Add depending if parent_key/type combination exists'''
		# Check if type already exists for parent_key
		for entry in cls.query(cls.type==type, ancestor=parent_key):
			# Type already exists so perform an update
			cls.update_model(entry, **kwargs)
			break
		# New entry
		else:
			entry = cls(parent=parent_key, type=type, **kwargs)
			entry.put()
		return entry

class Address(ContactDetailType):
	line = ndb.StringProperty()
	city = ndb.StringProperty()
	country = ndb.StringProperty()
	
class Email(ContactDetailType):
	email = ndb.StringProperty()
	
class User(ndb.Model, NdbUtilMixIn):
	user_name = ndb.StringProperty(required=True, indexed=True)
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	
	def _check_key(self):
		if self.key is None:
			raise ValueError("No key found for '%s'.  Make sure to invoke .put() first." % self.__class__.__name__)

	def add_address(self, type, **kwargs):
		self._check_key()
		Address.set(self.key, type=type, **kwargs)
	
	def add_email(self, type, **kwargs):
		self._check_key()
		Email.set(self.key, type=type, **kwargs)
	
	@classmethod
	def get_by_user_name(cls, user_name):
		return cls.get_first(cls.user_name == user_name)
	
	@classmethod
	def set(cls, **kwargs):
		'''Perform 'update' or 'add' depending if user_name already exists'''
		try:
			user_name = kwargs["user_name"]
		except KeyError:
			raise ValueError("Required attribute 'user_name' not provided.")

		entry = cls.get_by_user_name(user_name)
		if entry:
			cls.update_model(entry, **kwargs)
		else:
			# Create New
			entry = cls(**kwargs)
			entry.put()
		return entry
			
	@classmethod
	def get_user_dict(cls, user_name):
		user_entry = cls.get_by_user_name(user_name)
		if user_entry:
			user = user_entry.to_dict()
			user["id"] = user_entry.key.urlsafe()
			
			addresses = []
			for addr in Address.query(ancestor=user_entry.key):
				addr_dict = addr.to_dict()
				addr_dict["id"] = addr.key.urlsafe()
				addresses.append(addr_dict)
			user["addresses"] = addresses
			
			emails = []
			for email in Email.query(ancestor=user_entry.key):
				email_dict = email.to_dict()
				email_dict["id"] = email.key.urlsafe()
				emails.append(email.to_dict())
			user["emails"] = emails
			
			return user


#
# Model Instance.  Nested Model creation
#
user01 = User.set(user_name="marcos", first_name="Marcos", last_name="Lin")
user01.put()
user01.add_address(type="work", city="London", country="UK")
user01.add_address(type="home", city="Rome", country="Italy")
user01.add_email(type="work", email="marcos.work@example.com")
user01.add_email(type="home", email="marcos.home@example.com")
user01.add_email(type="work", email="work.marcos@example.com")
display_entity(user01)

#
# Model Instance.  Nested Model creation
#
user02 = User(user_name="flavia", first_name="Flavia", last_name="Bian")
user02.put()
user02.add_address(type="home", city="London", country="UK")
user02.add_address(type="home", city="Rome", country="Italy")
user02.add_email(type="home", email="marcos.home@example.com")
user02.add_email(type="home", email="flavia.home@example.com")
display_entity(user02)


#
# Make updating a single field
#
user03 = User.get_by_user_name("marcos")
user03.update(last_name="LLin")

#
# Returning entire User record
#
user_marcos = User.get_user_dict("marcos")
print "# Dictionary Version of 'marcos':"
pprint_dict(user_marcos)

#
# Query by urlsafe
#
address_id = user_marcos["addresses"][0]["id"]
print "# Querying by ID: %s" % address_id
address01 = ndb.Key(urlsafe=address_id).get()
if isinstance(address01, Address):
	print "# Confirmed class: %s" % address01.__class__.__name__

display_entity(address01)

#
# Query by urlsafe from wrong entity
#
try:
	email01 = Email.query_by_urlsafe(address_id)
except ValueError:
	print "# Expected ValueError raised when using Email class to retrieve an Address record."

# ALL
if False:
	display_all(User)
	display_all(Address)
	display_all(Email)
