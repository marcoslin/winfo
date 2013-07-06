#!/usr/bin/env python

import pprint

pp = pprint.PrettyPrinter(indent=2)
def pprint_dict(in_dict):
	pp.pprint( in_dict )

def display_entity(entity, header = "# -----------------------"):
    print header
    if entity is None:
        print "# Entity is NONE"
    else:        
        key = entity.key
        if key is None:
            print "# id: Key not available."
        else:
            parent = key.parent()
            if parent:
                print "# parent: %s" % parent
            print "# key: kind = %s; id = %s; urlsafe = %s" % (key.kind(),key.id(),key.urlsafe())
        pprint_dict( entity.to_dict() )
        print "#"

def display_all(model):
    print "\n\n\n"
    entry_count = 0
    for entity in model.query():
        entry_count += 1
        header = "# ###### Entry %d #######" % entry_count
        display_entity(entity, header)
