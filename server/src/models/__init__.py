import json
import datetime
from google.appengine.ext import ndb

# Turn on debug mode, bascially press the JVP
MODELS_DEBUG = True

#
# Define Exceptions
#
class NdbModelExceptions(StandardError):
    pass

class UnAuthorizedException(NdbModelExceptions):
    pass

#
# ndb.Model related
#
class NdbUtilMixIn(object):
    '''
    This MixIn allow updating of entities using key
    '''
    _skip_update_columns = None
    
    @classmethod
    def update_model(cls, model, **kwargs):
        #print "update_model [%s]: %s" % (cls.__name__, cls._skip_update_columns)
        for key in kwargs:
            if cls._skip_update_columns:
                if key in cls._skip_update_columns:
                    # Skip the updating of the key
                    continue
            setattr(model,key,kwargs[key])
        model.put()
        return model
    
    @classmethod
    def query_by_urlsafe(cls, urlsafe_id):
        entry = ndb.Key(urlsafe=urlsafe_id).get()
        if entry:
            if isinstance(entry, cls):
                return entry
            else:
                raise ValueError("urlsafe_id passed is a '%s' but current class is '%s'" % (entry.__class__.__name__, cls.__name__))

    @classmethod
    def update_by_urlsafe(cls, urlsafe_id, **kwargs):
        entry = cls.query_by_urlsafe(urlsafe_id)
        if entry:
            entry.update(**kwargs)
            return entry

    @classmethod
    def get_first(cls, *args):
        '''Return first record'''
        for entry in cls.query(*args):
            return entry

    def update(self, **kwargs):
        '''Instance method used to update a Model'''
        return self.update_model(self, **kwargs)
        
    #
    # Method used by RESTDaoBase to generate identifier as specified by _identifier_name
    #
    def get_identifier(self):
        '''Default to urlsafe version of the key'''
        return self.key.urlsafe()
    @classmethod
    def query_by_identifier(cls, in_identifier, parent=None):
        '''Method that works with `get_identifier` which by default uses urlsafe version of the key'''
        if parent is None:
            return cls.query_by_urlsafe(in_identifier)
        else:
            return cls.query_by_urlsafe(in_identifier, parent=parent)
    

#
# REST related
#
class Z1kJsonEncoder(json.JSONEncoder):
    '''
    Basic Encoder designed to convert datetime object into ISODATE
    '''
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, ndb.Key):
            return obj.id()
        else:
            return super(Z1kJsonEncoder, self).default(obj)


class RESTDaoBase(object):
    # Set the NDB Model.  Must Implement NdbUtilMixIn
    _ndb_model = None
    # Set to something like "_id" to auto populate it with entity.key.id()
    _identifier_name = None 
    # Set the column name that should be skipped 
    _skip_update_columns = None

    def _JVP(self):
        '''
        Address JSON Vulnerability Protection JVP as per AngularJS's documentation on $http:
        
        A JSON vulnerability allows third party website to turn your JSON resource URL into JSONP request under some conditions.
        To counter this your server can prefix all JSON requests with following string ")]}',\n". Angular will automatically strip
        the prefix before processing it as JSON.
        '''
        if MODELS_DEBUG:
            return ""
        else:
            return ")]}',\n"
    
    def _convert_to_json(self, in_dict):
        return json.dumps(in_dict, cls=Z1kJsonEncoder)
        
    def query(self, order_by=None, query_result=None):
        '''Return all entries.  Allow passing result of query, in which case the order_by is ignored'''
        first_row = True
        yield self._JVP()
        yield "["
        
        if query_result is None:
            if order_by:
                entry_generator = self._ndb_model.query().order(order_by)
            else:
                entry_generator = self._ndb_model.query().order()
        else:
            entry_generator = query_result
            
        for entry in entry_generator:
            res_dict = entry.to_dict()
            if self._identifier_name:
                res_dict[self._identifier_name] = entry.get_identifier()
            jstr = self._convert_to_json(res_dict)
            if first_row:
                yield jstr
                first_row = False
            else:
                yield ", %s" % jstr
        yield "]"
        
    def add(self, json_data, parent=None, set_id_as_identifier=False):
        '''Add an entry, optinally setting the id property'''
        if json_data:
            if parent is not None:
                json_data["parent"] = parent
            
            if set_id_as_identifier:
                try:
                    id_value = json_data[self._identifier_name]
                except KeyError:
                    raise ValueError("Attempting to set id as identifier but '%s' no found in the input." % self._identifier_name)
                entry = self._ndb_model(id=id_value, **json_data)
            else:
                entry = self._ndb_model(**json_data)
            
            entry_key = entry.put()
            res_dict = entry.to_dict()
            # Need to add ID to the result
            if self._identifier_name:
                res_dict[self._identifier_name] = entry.get_identifier()
            return self._JVP() + self._convert_to_json(res_dict)
        
    def get(self, in_identity, in_entry=None):
        # Return a single row
        if in_entry is not None:
            entry = in_entry
        else:
            entry = self._ndb_model.query_by_identifier(in_identity)
            
        if entry:
            res_dict = entry.to_dict()
            if self._identifier_name:
                res_dict[self._identifier_name] = entry.get_identifier()
            return self._JVP() + self._convert_to_json(res_dict)
        
    def update(self, in_identity, json_data, in_entry=None):
        if json_data is None:
            return None
        
        if in_entry is not None:
            entry = in_entry
        else:
            entry = self._ndb_model.query_by_identifier(in_identity)
                    
        if entry:
            entry.update(**json_data)
            # Return the updated model
            return self._JVP() + self._convert_to_json(entry.to_dict())
        
    def delete(self, in_identity, in_entry=None):
        if in_entry is not None:
            entry = in_entry
        else:
            entry = self._ndb_model.query_by_identifier(in_identity)
        entry.key.delete()
