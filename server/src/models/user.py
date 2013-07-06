from google.appengine.ext import ndb

from models import NdbUtilMixIn, RESTDaoBase

class User(ndb.Model, NdbUtilMixIn):
    _check_dup_and_raise_error = True
    _skip_update_columns = ("modified_on", "created_on")
    
    user_name = ndb.StringProperty(required=True, indexed=True)
    user_name_type = ndb.StringProperty(indexed=True, choices=("local","oauth"), default="local")
    
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    login_email = ndb.StringProperty()
    secure_passwd_hash = ndb.StringProperty()
    
    modified_on = ndb.DateTimeProperty(auto_now=True)
    created_on = ndb.DateTimeProperty(auto_now_add=True)

    def _pre_put_hook(self):
        '''
        Using pre update hook to ensure that no duplicated user_name is created.
        Can be skipped if _check_dup_and_raise_error is used.
        '''
        if self._check_dup_and_raise_error:
            cur_key = self.key
            for entry in self.query(User.user_name == self.user_name):
                # If cur_key exists, means that user performing update
                if cur_key:
                    if cur_key == entry.key:
                        continue
                    else:
                        raise ValueError("user_name '%s' is a duplicated entry." % (self.user_name))
                # If adding
                raise ValueError("user_name '%s' is a duplicated entry." % (self.user_name))

    @classmethod
    def set(cls, **kwargs):
        '''
        Perform 'update' or 'add' depending if user_name already exists.  As user_name is already
        being queried and checked, skip the _pre_put_hook check.
        '''
        try:
            user_name = kwargs["user_name"]
        except KeyError:
            raise ValueError("Required attribute 'user_name' not provided.")

        entry = cls.get_by_user_name(user_name)
        if entry:
            try:
                cls._check_dup_and_raise_error = False
                cls.update_model(entry, **kwargs)
            except:
                raise
            finally:
                cls._check_dup_and_raise_error = True
        else:
            # Create New
            entry = cls(**kwargs)
            try:
                cls._check_dup_and_raise_error = False
                entry.put()
            except:
                raise
            finally:
                cls._check_dup_and_raise_error = True
        return entry

    def _check_key(self):
        if self.key is None:
            raise ValueError("No key found for '%s'.  Make sure to invoke .put() first." % self.__class__.__name__)
    
    @classmethod
    def get_by_user_name(cls, user_name):
        return cls.get_first(cls.user_name == user_name)
            
    @classmethod
    def get_user_dict(cls, user_name):
        user_entry = cls.get_by_user_name(user_name)
        if user_entry:
            user = user_entry.to_dict()
            user["user_id"] = user_entry.key.urlsafe()
            
            # Create placeholder for deleted items
            user["deleted"] = { "emails": [], "addresses": [] }

            return user



class UserDao(RESTDaoBase):
    _ndb_model = User
    _skip_update_columns = ("modified_on", "created_on")
    _identifier_name = "user_id"
    
    def check_user_name_exists(self, user_name):
        entry = self._ndb_model.get_by_user_name(user_name)
        if entry is None:
            return False
        else:
            return True
    
    def get_user_dict(self, user_name):
        res_dict = self._ndb_model.get_user_dict(user_name)
        return self._JVP() + self._convert_to_json(res_dict)
    
    def save_user_dict(self, user_name, in_dict):
        # Get the User instance
        user_id = in_dict["user_id"]
        user = self._ndb_model.query_by_urlsafe(user_id)
                
        # Extract emails entry and update it
        emails = in_dict["emails"]
        for email in emails:
            user.add_email(**email)
        del in_dict["emails"]
    
        # Extract address entry and update it
        addresses = in_dict["addresses"]
        for addr in addresses:
            user.add_address(**addr)
        del in_dict["addresses"]
        
        # Delete emails and addresses
        deleted = in_dict["deleted"] 
        for del_email_id in deleted["emails"]:
            user.del_email(del_email_id)
        for del_addr in deleted["addresses"]:
            user.del_address(del_addr)
            
        # Update the remaing attributes
        return User.update_by_urlsafe(user_id, **in_dict)
        


