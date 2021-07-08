# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 16:05:08 2020

@author: akoyamparamb
"""


def log(line, writepath, login):
    if login == True:
        login = False
        logfile = open(writepath, "w+")
        logfile.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    else:
        logfile = open(writepath, "a")
    for i in line:
        logfile.write('\n'+str(i))
    logfile.close()