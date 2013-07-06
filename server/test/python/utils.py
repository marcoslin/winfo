
# Add path to the google_appengine
import dev_appserver
dev_appserver.fix_sys_path()

# Needed to run ndb locally
# REF: https://developers.google.com/appengine/docs/python/tools/localunittesting#Writing_Datastore_and_Memcache_Tests
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed
tb = testbed.Testbed()
tb.activate()
tb.init_datastore_v3_stub()
tb.init_memcache_stub()