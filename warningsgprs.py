# -*- coding: utf-8 -*-
"""
Created on Tue May 17 15:10:54 2022

@author: akoyamparamb
"""


"""
The class is an error class that shall be raised in order to break
an operation or close an operation. The users are free to modify this class.
BREAK THE CODE IF EXCEPT AN APIERROR
""" 
class APIError(Exception): 
    pass

class PRODError(Exception):
    pass
                
class IncompleteProcessFlow(Exception):
    pass

class InputError(Exception):
    pass