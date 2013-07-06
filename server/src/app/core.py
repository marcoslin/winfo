# -*- coding: utf-8 -*-
'''
Created on 21 May 2013

@author: Marcos Lin

Provide core utilities objects for the app.
'''

import os, sys, inspect
import logging
import json

import time, random, hashlib, base64


# ==============================================================================
# code debug print statement
def trace(*args):
    '''
    core.trace is light weight debug statement to be used for code that imports this package.
    To minimize unnecessary processing, make sure to pass a tuple of string to be joined upon
    trace output instead of creating the final string on the caller side.

    For trace statement in a heavily used code and/or loop, make sure to precede the trace
    statement with a 'if __debug__:' check allowing entire trace statement to be compiled out.
    In fact, if this module is compiled with optimization, trace will stop working.
    '''
    if __debug__:
        if ( sys.flags.debug ):
            filename = os.path.basename(inspect.stack()[1][1])
            caller = inspect.stack()[1][3]
            # Convert all args into string
            msgs = []
            for arg in args:
                if isinstance(arg, basestring):
                    msgs.append(arg)
                else:
                    msgs.append(str(arg))
            print "T.%s: %s (%s)" % (caller, ''.join(msgs), filename)

# ==============================================================================
# Singletons
class Singleton(type):
    '''
    Meta Class used to create a singleton.  Usage:
    
    def ClassObject(object):
        __metaclass__ = Singleton
        ...
    '''
    def __init__(cls, name, bases, dct):
        #print "### Singleton called for class %s" % name
        super(Singleton, cls).__init__(name, bases, dct)
        cls.instance = None 

    def __call__(cls, *args, **kwargs): #@NoSelf
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)
        #print "### Returning Singleton instance %s" % cls.instance
        return cls.instance

# ==============================================================================
# Config
class ConfigurationStore(object):
    '''
    Loads a json file and set all keys to be property of this object.  This is can used by
    Flask's configuration system '.config.from_object(<obj>)' that will read all UPPER CASE
    property of this and expose it via '.config["<key>"]' method.
    
    Key properties of this config:
    * APP: name of the application
    * INST: physical server location of deployed app
    * RUN_MODE: prod, qa, test, dev or utest
    * SHARD_ID: from shard.json file that maps APP/INST/RUN_MODE to an id
    
    By default, this object will look for an additional configuration, in the same directory
    as the configuration file provided, named 'local.json'.  This is to allow local development
    override.
    '''
    __metaclass__ = Singleton
    _local_json = "local.json"
    _logger = None
    SHARD_ID = 0
    
    def __init__(self, in_json_file=None, in_local_json_file=None, logger=None):
        '''
        Loads the json_file provided and, if exists, loads the override file named 'local.json'
        in the same directory as the json_file.
        '''
        # Set logger
        if logger:
            self._logger = logger
            
        # Set json files
        json_file = self._search_config(in_json_file)
        self._config_dir = os.path.dirname(json_file)
        self.__apply_json_config(json_file)
        
        # Look for local.json file
        if in_local_json_file is None:
            in_local_json_file = self._local_json

    
    @property
    def config_dir(self):
        return self._config_dir
    
    @property
    def logger(self):
        if self._logger:
            return self._logger
        elif hasattr(self, "LOGGER_NAME"):
            return logging.getLogger(self.LOGGER_NAME)
        else:
            raise ValueError("Failed to obtain logger.  Make sure LOGGER_NAME attribute is set in the configuration file.")

    def __apply_json_config(self, json_file):
        '''
        Open the json file and make the key become the attribute of the object,
        ignoring the keys starting with '_'
        '''
        json_data = self.load_json_file(json_file)
        for key in json_data:
            if not key.startswith("_"):
                self.apply_config(key, json_data[key])

    def apply_config(self, key, value):
        self.__dict__.update({key: value})

    def apply_shard_json(self, shard_json_file):
        '''
        Load the shard.json config file from the config directory.
        '''
       
        # Load config file
        config_file = os.path.join(self._config_dir, shard_json_file)
        shard_json = self.load_json_file(config_file)
        try:
            shard_config = shard_json["SHARD_CONFIG"]
        except KeyError:
            raise ValueError("Missing configuration entry 'SHARD_CONFIG' from the '%s' file." % config_file)
        
        # Look for shard_id
        shard_id = 0
        wild_card = "*"
        for entry in shard_config:
            if (
                entry["APP"] == self.APP
                and entry["RUN_MODE"] == self.RUN_MODE
                and ( entry["INST"] == wild_card or entry["INST"] == self.INST )
            ):
                shard_id = entry["shard_id"]
        
        self.SHARD_ID = shard_id

    @classmethod
    def _search_config(cls, json_file, script_dir=os.path.dirname(os.path.realpath(__file__))):
        '''
        This method searches for file in the ../config directory from the current script directory in the order:
           a. dev.json
           b. config.json
           c. app.json
        
        The @classmethod decoration allow for this method to be unit tested
        '''
        
        # Return json file passed
        if json_file:
            return json_file
        
        # search for config named dev.json, config.json or app.json
        # intentionally not searching for qa.json, utest.json and prod.json
        for file_name in ("dev.json", "config.json", "app.json"):
            config_file = os.path.join(script_dir, "../config", file_name)
            if os.path.exists(config_file):
                return config_file
            
        # If not found
        return None
    
    @classmethod
    def load_json_file(cls, json_file):
        '''Load json file and return a dictionary'''
        if not os.path.exists(json_file):
            raise IOError("Failed to load '%s' json file as it does not exists." % json_file)
        with open(json_file, "r") as fh:
            try:
                return json.load(fh)
            except ValueError as e:
                raise IOError("Failed to parse '%s' as json.  Error from parser: %s" % (json_file, e))
        
    @classmethod
    def unload(cls):
        '''Setting the class' instance to None forcing the re-initialization.'''
        trace("Unloading ConfigurationStore")
        ConfigurationStore.instance = None
    
    #      
    # Allow the use of with statement
    #
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ==============================================================================
# Hash
class HashUtils(object):
    '''
    Hash Utilities Library used to create password hash and generate unique tokens.
    The salt and pepper property is set from configuration file via `__new__`.
    
    All methods support a `output` paramenter, that can be set to:
    * hex = base 16 encoding
    * b32 = base 32 encoding
    * b64_url = URL safe base64 encoded string
    * b64 = normal base64 encoding
    `b64` is the default if `output` is not set
    
    '''
    hash_salt = None
    hash_pepper = None
    
    def __new__(cls, *args, **kwargs):
        '''This is used so that hash_salt and hash_pepper is set at cls level, which will be pushed down to instance'''
        if cls.hash_salt is None or cls.hash_pepper is None:
            with ConfigurationStore() as conf:
                try:
                    cls.hash_salt = conf.AUTH_PASSW_SALT
                except:
                    raise RuntimeError("Missing required 'AUTH_PASSW_SALT' configuration entry required for HashUtils.")
                try:
                    cls.hash_pepper = conf.AUTH_PASSW_PEPPER
                except:
                    raise RuntimeError("Missing required 'AUTH_PASSW_PEPPER' configuration entry required for HashUtils.")
        return super(HashUtils, cls).__new__(cls,*args, **kwargs)

    @classmethod
    def _encode_digest(cls, in_digest, size=None, output=None):
        '''Translate output to base64 functions'''

        # Translate output to base64 encoding scheme
        cv_lower = False
        if output=="hex":
            enc = base64.b16encode
            cv_lower = True
        elif output=="b32":
            enc = base64.b32encode
        elif output=="b64_url":
            enc = base64.urlsafe_b64encode
        elif output=="digest":
            enc = None
        else: # Assume b64
            enc = base64.b64encode
        
        # Truncate result
        if size:
            if size < 1:
                size = 1
            if size > len(in_digest):
                size = len(in_digest)
            in_digest = in_digest[0:size]

        # Only encode if enc set
        if enc is None:
            return in_digest
        else:
            encoded = enc(in_digest)
            # Format the result
            if cv_lower:
                return encoded.lower()
            else:
                return encoded
    
    @classmethod
    def _create_digest(cls, algorithm, *args, **kwargs):
        '''
        Create hash digest in the specified algorithm, which can be:
        * md5, sha1, sha256, sha512
        '''
        
        # Translate algorithm to md5
        if algorithm=="md5":
            hash_alg = hashlib.md5
        elif algorithm=="sha1":
            hash_alg = hashlib.sha1
        elif algorithm=="sha256":
            hash_alg = hashlib.sha256
        elif algorithm=="sha512":
            hash_alg = hashlib.sha512
        
        # Extract output from kwargs
        try:
            output = kwargs["output"]
        except:
            output = None

        if args:
            if len(args) == 1:
                in_str = args[0]
            else:
                in_str = "".join(args)
                
            if isinstance(in_str, unicode):
                in_str = in_str.encode("utf-8")

            dgst = hash_alg(in_str).digest()
            
            return cls._encode_digest(dgst, output=output)
        else:
            # Empty input so return None
            return None

    @classmethod
    def create_sha1_hash(cls, *args, **kwargs):
        '''Return encoded sha1 hash.  Accepts 'output' kwargs option.'''
        return cls._create_digest("sha1", *args, **kwargs)

    @classmethod
    def create_md5_hash(cls, *args, **kwargs):
        '''Return encoded sha1 hash.  Accepts 'output' kwargs option.'''
        return cls._create_digest("md5", *args, **kwargs)

    def secure_hash(self, *args, **kwargs):
        '''
        Intention of this method is to create secure hash serving as password hash or key
        from unknown source.
        
        Uses sha1 to prevent collision and b64encode for speed
        '''
        if args:
            vals = [self.hash_salt]
            vals.extend(args)
            vals.append(self.hash_pepper)
            return self._create_digest("sha1", *vals, **kwargs)
        else:
            return None
    
    def _random_digest(self):
        '''Generate random SHA1 digest with time and a random integers'''
        rand = str(random.getrandbits(64))
        time_str = str(time.time())
        vals = (self.hash_pepper, time_str, self.hash_salt)
        return hashlib.md5(rand.join(vals)).digest()

    def generate_token(self, size=None, output=None):
        '''Return random token.  This is 2.1x faster than generate_token_url.'''
        dgst = self._random_digest()
        res = self._encode_digest(dgst, size=size, output=output)
        if res.endswith("="):
            return res.rstrip("=")
        else:
            return res

    def generate_token_url(self, size=None):
        '''Return random token usable in the URL.  This is method is 80% faster than idgen's 64bit ID.'''
        return self.generate_token(size=size, output="b64_url")
