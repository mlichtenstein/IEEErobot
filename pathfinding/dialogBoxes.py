import easygui
from easygui import *
import sys

msg = "Enter logon information"
title = "Demo of multpasswordbox"
fieldNames = ["Server ID", "User ID", "Password"]
fieldValues = []  # we start with blanks for the values
fieldValues = multpasswordbox(msg,title, fieldNames)

# make sure that none of the fields was left blank
while 1:
    if fieldValues == None: break
    errmsg = ""
    for i in range(len(fieldNames)):
        if fieldValues[i].strip() == "":
            errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "": break # no problems found
    fieldValues = multpasswordbox(errmsg, title, fieldNames, fieldValues)
writeln("Reply was: %s" % str(fieldValues))
