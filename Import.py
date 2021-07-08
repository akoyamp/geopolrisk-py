# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 15:54:49 2020

@author: akoyamparamb
"""
import sys
import subprocess
import pkg_resources

required = {'pandas', 'numpy', 'openpyxl', 'datetime', 'math'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)


