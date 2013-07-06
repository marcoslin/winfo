'''
Created on 17 Jun 2013

@author: Marcos Lin

Load the current directory as a sys.path
'''

import os, sys

lib_dir = os.path.dirname(__file__)
sys.path.append(lib_dir)
