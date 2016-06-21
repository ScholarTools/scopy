# -*- coding: utf-8 -*-
"""
"""

#Standard library
import os
import inspect

# http://stackoverflow.com/questions/50499/in-python-how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executin/50905#50905
package_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_path = os.path.split(package_path)[0]

class Config(object):
    
    def __init__(self):
        api_path = os.path.join(root_path,'api_key.txt')
        with open(api_path, 'r') as file:
            self.api_key = file.read()

