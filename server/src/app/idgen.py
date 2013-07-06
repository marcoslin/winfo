'''
Created on 5 Feb 2013

@author: Marcos Lin

This library creates id at the length specified.
'''

from app.core import trace, Singleton, ConfigurationStore
from google.appengine.api import memcache
import time

# Singleton
class IDGenerator(object):
    '''
    Singleton Identity Generator.
    Note: domain is equivalent to a column name that needs a unique ID
    '''
    __metaclass__ = Singleton
    def __init__(self, output=None):
        '''
        output supported:
        * int: to unsigned integer (Default)
        * signed: to signed integer
        '''
        trace("Initialized")
        self.cache = memcache
        self._output = output
        
        self._ig48 = IdentityGenerator(self.cache)
        self._ig64 = Id64Generator(self.cache)
        
        config = ConfigurationStore()
        self.shard_id = config.SHARD_ID
        
    def id48(self, domain, shard_id=None):
        '''Generate a 48bit integer for a given domain'''
        if shard_id is None:
            shard_id = self.shard_id
        return self._generate_id(self._ig48, domain, shard_id)
    
    def id64(self, domain, shard_id=None):
        '''Generate a 64bit integer for a given domain'''
        if shard_id is None:
            shard_id = self.shard_id
        return self._generate_id(self._ig64, domain, shard_id)
    
    def _generate_id(self, id_generator, domain, shard_id):
        genid = id_generator.generate_id(domain, shard_id)
        if self._output == "signed":
            # Basically, substract to minimum number of a signed integer
            # based on the number of the bit of identity.  A negative integer
            # has the left most bit of 1.  So a 4 bit number of -1 is 1001
            nbits = id_generator.identity_bits
            nbits_min = (1 << (nbits-1))
            return genid - nbits_min
        else:
            return genid





# Generator class
class IdentityGenerator(object):
    '''
    Generate a 48 bit ID where:
    *  1 bit for id type.  1 = Server Generated Id, 2 = Client Generated
    * 31 bit leading represent seconds since EPOCH.  This should be good for 68 years.
    *  8 bit counter for max of 256 IDs per second
    *  8 bit shard id for 256 different installations
    '''
    
    # CounterRetryError is not expected to be called other classes
    class CounterRetryError(OverflowError):
        '''
        Error raise when counter reached the highest allocated integer but that
        caller should retry 
        '''
        pass
    
    # Inspired by Instagram 
    # http://www.tumblr.com/ZElL-wA6vd-t
    
    # Custom Epoch set for 1 Jan 2013
    # print time.mktime( datetime.date(2013,1,1).timetuple() )
    # ToDo: Create a check and log a warning if withing 2 year of reaching Overflow for leading based on EPOCH below
    EPOCH = 1356998400.0

    # The last part of ID cannot be change as all ID generated must ends with the 8 bit shard_id 
    _SHARD_BITS = 8

    # Following entries can be overridden to create custom ID generator
    IDTYPE_BITS = 1
    LEADING_BITS = 31
    COUNTER_BITS = 8
    RESERVED_BITS = 0
    
    # Following entry should be changed according to what is returned by _get_leading.  Default to 1 second
    SLEEP_TIME = 1

    def __init__(self, cache):
        self.cache = cache
        # Compute the max value 
        self._max_leading = self._calc_max_int(self.leading_bits)
        self._max_counter = self._calc_max_int(self.counter_bits)
        self._max_shard = self._calc_max_int(self.shard_bits)

    # Properties about different components of the identity
    @property
    def idtype_bits(self):
        return self.IDTYPE_BITS
    @property
    def leading_bits(self):
        return self.LEADING_BITS
    @property
    def counter_bits(self):
        return self.COUNTER_BITS
    @property
    def reserved_bits(self):
        return self.RESERVED_BITS
    @property
    def shard_bits(self):
        return IdentityGenerator._SHARD_BITS
    @property
    def identity_bits(self):
        return self.idtype_bits + self.leading_bits + self.counter_bits + self.reserved_bits + self.shard_bits
    
    # Other properties
    @property
    def shard_mask(self):
        return self._max_shard
    
    # Private Function
    @classmethod
    def _calc_max_int(cls, bits):
        '''
        Return the max number of integer given the bits.
        bits must be between 0 to 64 or ValueError will be raised.
        '''
        if bits < 0:
            raise ValueError("Failed to return max integer number.  Bits must be greater than zero.")
        elif bits > 64:
            raise ValueError("Failed to return max integer number.  Bits must be less than 64.")
        elif bits == 0:
            return 0
        else:
            res = ( 2 ** bits ) - 1
        return res

    def _get_leading(self, shard_id, domain):
        '''
        Function to return leading part of the id.  By default, it returns seconds
        since the custom EPOCH attribute.  Override to return custom leading part
        of the identity generated.
        '''
        custom_epoch = time.time() - IdentityGenerator.EPOCH
        return int(custom_epoch)

    def _get_increment(self, shard_id, domain):
        '''
        Return tuple with leading, counter.
        '''
        # Initialize key variable
        leading_key = "%s.%s.%s:%d" % ("LEAD", self.__class__.__name__, domain, shard_id)
        counter_key = "%s.%s.%s:%d" % ("COUNT", self.__class__.__name__, domain, shard_id)
        leading = None
        leading_dup = False
        counter = 0
        
        # Get the leading and check if previously used.  If yes, set leading_dup to True
        # If leading_bits not allocated, set the leading to None
        if self.leading_bits:
            # Check of Overflow is performed here make it easier to override the _get_leading
            leading = self._get_leading(shard_id, domain)
            
            # Make sure that leading does not exceed the bit allocated for it
            if leading > self._max_leading:
                raise OverflowError("Identity exceeded maximum allocated number with leading of %s" % leading)
            
            # Check if previously used
            cached_leading = self.cache.get(leading_key)
            if leading == cached_leading:
                trace("LEADING DUP")
                leading_dup = True
            else:
                # Not dup, store the leading and reset the counter
                trace("LEADING NEW")
                self.cache.set(leading_key, leading)
                self.cache.set(counter_key, counter)

        # Counter should be generate if leading is a dup or if leading_bits is not allocated
        if leading is None or leading_dup:
            # Retrieve the previous counter used
            cached_counter = self.cache.get(counter_key)
            if cached_counter is not None:
                counter = cached_counter
                
            # Increment counter
            trace("Counter PRE %d" % counter)
            counter += 1
            trace("Counter Incremented to %d" % counter)
            # If max counter reached and leading_bits allocated, raise the CounterRetryError
            if counter >= self._max_counter:
                if self.leading_bits:
                    raise self.CounterRetryError("Max counter integer of %d reached" % counter)
                else:
                    raise OverflowError("Identity exceeded maximum allocated number with counter of %s" % counter)
            # Store the previous counter used
            self.cache.set(counter_key, counter)
        
        return (leading, counter)
    
    # Return the ID
    def generate_id(self, domain, shard_id):
        '''
        Generate the identity made of leading + counter + shard.
        * Leading is generally time based value and if it has not changed since the previous call,
          counter will be incremented.  If counter exceeds allocated bits, CounterRetryError will
          be raised.  Generally, caller should catch CounterRetryError, sleep and then call
          generate_id again.
        * If leading or shard exceed the allocated bits, OverflowError will be raised.
        '''
        
        # Retrive the shard to be used
        if shard_id > self._max_shard:
            raise OverflowError("Shard exceeded the allocated bit.  Shard returned: %s" % shard_id)
        
        # Get the leading and counter
        search_increment = True
        while search_increment:
            try:
                leading, counter = self._get_increment(shard_id, domain)
                search_increment = False
            except self.CounterRetryError:
                if self.SLEEP_TIME:
                    trace("CounterRetryError raised.  Sleeping for ", self.SLEEP_TIME, " seconds before retry.")
                    # ToDo: Figure out how to do the lag.warn
                    #log.warn("Sleeping for %s seconds..." % self.SLEEP_TIME)
                    time.sleep(self.SLEEP_TIME)
                else:
                    trace("CounterRetryError raised.  Retrying without sleep.")
        
        # Pack the part into a integer to form identity
        genid = 0
        shift_bits = self.identity_bits
        trace("Generating id of %d bits with:" % shift_bits)
        
        if self.idtype_bits:
            shift_bits -= self.idtype_bits
            genid |= 1 << shift_bits
            trace("* ", self.idtype_bits, ", shift by ", shift_bits, ", bits for idtype: ", 1)
        
        if self.leading_bits:
            shift_bits -= self.leading_bits
            genid |= leading << shift_bits
            trace("* ", self.leading_bits, ", shift by ", shift_bits, ", bits for leading: ", leading)
        
        if self.counter_bits:
            shift_bits -= self.counter_bits
            genid |= counter << shift_bits
            trace("* ", self.counter_bits, ", shift by ", shift_bits, ", bits for counter: ", counter)

        if self.reserved_bits:
            shift_bits -= self.reserved_bits
            trace("* ", self.reserved_bits, ", shift updated to ", shift_bits, " for reserve.")

        if self.shard_bits:
            genid |= shard_id
            trace("* ", self.shard_bits, ", no shift, bits for shard: ", shard_id)
        
        return genid
    
    # Debug Function
    def binary_id_breakdown(self, identity):
        '''Code used to perform the breaking of binary parts'''
        bin_id = str(bin(identity))[2:]
        
        res_bin = []
        start_pos = 0
        end_pos = 0
        
        for x in (self.idtype_bits, self.leading_bits, self.counter_bits, self.reserved_bits, self.shard_bits):
            end_pos = start_pos + x
            s = bin_id[start_pos:end_pos]
            s_bin = "0b" + s
            trace("binary: ", s_bin, ", int: ", int(s_bin,0))
            res_bin.append(s)
            trace("Start:", start_pos, ", end:", end_pos)
            start_pos = end_pos
        
        return " ".join(res_bin)

class Id16Generator(IdentityGenerator):
    '''
    Generate a 16 bit ID where:
    *  1 bit for id type.  1 = Server Generated Id, 2 = Client Generated
    *  0 bit leading.
    *  7 bit counter for max of 128 IDs
    *  8 bit shard id for 256 different installations

    N.B.: This should ONLY BE USED FOR UNIT TESTING.  The intention here is to
          create a generator where Overflow can be testd.
          
    Note: Server as sample of counter only ID generator is designed but in prod
          the counter storage must be on a permanent storage instead of cache
    '''

    LEADING_BITS = 0
    COUNTER_BITS = 7
    
class Id64Generator(IdentityGenerator):
    '''
    Generate a 64 bit ID where:
    *  1 bit for id type.  1 = Server Generated Id, 2 = Client Generated
    * 42 bit leading represent seconds since EPOCH.  This should be good for 139 years.
    * 10 bit counter for max of 1024 IDs per millisecond
    *  3 bit reserved for future shard requirement
    *  8 bit shard id for 256 different installations
    '''

    LEADING_BITS = 42
    COUNTER_BITS = 10
    RESERVED_BITS = 3
    
    # As leading is set to be milliseconds, sleep for .01 seconds only
    SLEEP_TIME = 0.01
    
    def _get_leading(self, shard_id, domain):
        '''
        Override the method to return milliseconds instead of seconds
        '''
        custom_epoch = time.time() - IdentityGenerator.EPOCH
        # Returning milliseconds since the custom epoch
        return int(custom_epoch * 1000)
