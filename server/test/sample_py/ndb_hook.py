#!/usr/bin/env python

import sys
sys.path.append("../python/")
import utils

from google.appengine.ext import ndb
from pprint_ndb import display_entity, display_all

#
# DEFINE MODELS
#
class TestContact(ndb.Model):
	_check_dup_and_raise_error = True
	
	user_name = ndb.StringProperty(required=True, indexed=True)
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	city = ndb.StringProperty()
	modified_on = ndb.DateTimeProperty(auto_now=True)
	created_on = ndb.DateTimeProperty(auto_now_add=True)
	
	def _pre_put_hook(self):
		# Check for dups
		if self._check_dup_and_raise_error:
			print "!!! pre_put called"
			cur_key = self.key
			for entry in self.query(TestContact.user_name == self.user_name):
				print "Examining entry: ", entry
				# If updating
				if cur_key:
					if cur_key == entry.key:
						print "!!! Updating"
						continue
					else:
						raise ValueError("Dup Entry.")
				# If adding
				raise ValueError("Dup Entry.")

	@classmethod
	def set(cls, user_name, **kwargs):
		'''Update or Add depending if parent_key/type combination exists'''
		# Check if type already exists for parent_key
		for entry in cls.query(cls.user_name == user_name):
			# Type already exists so perform an update
			try:
				cls._check_dup_and_raise_error = False
				cls.update_model(entry, **kwargs)
			except:
				raise
			finally:
				cls._check_dup_and_raise_error = True
			break
		# New entry
		else:
			entry = cls(user_name=user_name, **kwargs)
			try:
				cls._check_dup_and_raise_error = False
				entry.put()
			except:
				raise
			finally:
				cls._check_dup_and_raise_error = True

		return entry

	@classmethod
	def update_model(self, model, **kwargs):
		for key in kwargs:
			setattr(model,key,kwargs[key])
		model.put()

	@classmethod
	def query_country(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key)


print "\n# Saving user 'marcos' using ndb Standard"
marcos = TestContact(user_name="marcos", first_name="Marcos", last_name="Lin")
marcos.put()

print "\n# Saving user 'flavia' using set"
flavia = TestContact.set(user_name="flavia", first_name="Flavia", last_name="Bian")

print "\n# Attempting to create a dup using update"
marcos.user_name = "flavia"
try:
	marcos.put()
except ValueError:
	print "-> Expected ValueError."
else:
	raise RuntimeError("ValueError expected.")

print "\n# Creating a dup 'marcos' user"
user01 = TestContact(user_name="marcos", first_name="Xxx", last_name="Yyy")
print "# Saving user01"
try:
	user01.put()
except ValueError:
	print "-> Expected ValueError."
else:
	raise RuntimeError("ValueError expected.")


print "\n# Updating user 'flavia' using ndb Standard"
for entry in TestContact.query(TestContact.user_name=="flavia"):
	entry.last_name="Xxxx"
	entry.put()


print "\n# Updating user 'flavia' using set"
TestContact.set('flavia', last_name="Lin")


display_all(TestContact)
