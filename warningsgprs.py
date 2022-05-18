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
        
# class FUNCError(Exception):
#     def __init__( e = None):
#         error = ["OutputFile", "SQLFile", "PLTError" ]
#         self.error = e if e in error else ": Refer log file"
#         print("Error in the functionality", self.error)
        
class IncompleteProcessFlow(Exception):
    pass

class InputError(Exception):
    pass