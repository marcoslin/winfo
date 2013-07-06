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
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    city = ndb.StringProperty()
    modified_on = ndb.DateTimeProperty(auto_now=True)
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    
    @classmethod
    def query_country(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key)


class TestBook(ndb.Model):
    book_name = ndb.StringProperty()
    contact_keys = ndb.KeyProperty(kind=TestContact, repeated=True)

#
# Create simple entry
#
entry01 = TestContact(first_name="Marcos", last_name="Bin")
entry01.put()
display_entity(entry01)

#
# Create entry with id
#
entry02 = TestContact(id=54321, first_name="Read", last_name="Lines")
#entry02.parent = entry01.key
entry02.put()
display_entity(entry02)


#
# Create entry with a Country as a parent.  Note that key must be added to a record using the parent
# property and parent cannot be updated once set.
# http://stackoverflow.com/questions/11854137/how-to-change-ancestor-of-an-ndb-record
#
country_key = ndb.Key("Country", "Italy")
entry03 = TestContact(parent=country_key, first_name="Flavia", last_name="Bin", city="Rome")
entry03.put()
display_entity(entry03)

entry03a = TestContact(id=123, parent=country_key, first_name="Giulia", last_name="Bin", city="Rome")
entry03a.put()

#
# Query by Country.  Make sure that it returns both records added
#
countryITA_key = ndb.Key("Country", "Italy")
entry04s = TestContact.query_country(countryITA_key)
for entry04 in entry04s:
    display_entity(entry04, "# -- Country -------------")

entry03a_ita = ndb.Key("Country", "Italy", TestContact, 123).get()
display_entity(entry03a_ita)
if entry03a_ita.parent == countryITA_key:
    print "Ancestor Matches!!!"

#
# Trying to put another item with same id.  The record should be updated.
# Note that id is set upon creation and cannot be modified once estabilished.
# Setting id after instanciation does not work, as per line: entry02.id = 54321
#
entry02 = TestContact(id=54321, first_name="Read2", last_name="Lines2")
#entry02.id = 54321
entry02.put()
display_entity(entry02)

bookA = TestBook(book_name="BookA", contact_keys=(entry01.key, entry02.key, entry03.key))
bookA.put()

bookB = TestBook(book_name="BookB", contact_keys=(entry03.key, entry03.key, entry03a.key))
bookB.put()

display_entity(bookA, "# -- BookA Pre -----------")
display_entity(bookB, "# -- BookB Pre -----------")


# Delete all entries
e03 = bookA.contact_keys[2]

bookA.contact_keys.remove(entry03.key)
bookA.put()
for e in bookB.contact_keys:
    try:
        bookB.contact_keys.remove(entry03.key)
    except:
        break
bookB.put()

entry03.key.delete()

print "E03: ", e03.get()
display_entity(bookA, "# -- BookA Post ----------")
display_entity(bookB, "# -- BookB Post ----------")

#
# Illustrate that key is a base64 encoded list
#
print "\n# Key Test"
key01 = ndb.Key("User", 1)
print "-  key01: %s" % key01.urlsafe()
key02 = ndb.Key("UserThatIsVeryLongWork", 112313124321421342, "PathAlsoLotsOfCharactersInIT", "ALongIDUsedJustTOseeHowTHisWorks")
print "-  key02: %s" % key02.urlsafe()

#
# Display All
#
display_all(TestContact)
