import easygui
from easygui import *
import sys

def editNode(node):
    msg = "Node " + str(node)
    title = "Edit node " + str(node) +"'s data"
    fieldNames = ["X position", "Y position", "theta to grab puck at", "puck it can access 0-15 (-1 for None)", "radius of acceptability", "localize?"]
    fieldValues = [node.X,node.Y,node.theta,node.puck, node.radius, node.localize]
    fieldValues = multenterbox(msg,title, fieldNames, fieldValues)
    if fieldValues == None:
        return False
    node.X = int(fieldValues[0])
    node.Y = int(fieldValues[1])
    node.theta = int(fieldValues[2])
    node.puck = int(fieldValues[3])
    node.radius = int(fieldValues[4])
    node.localize = int(fieldValues[5])
    return True

def editLink(link):
    msg = "Link " + str(link)
    title = "Edit link " + str(link) +"'s data"
    fieldNames = ["crossed log (0/1)", link.node1h+" "+link.node1v+" nodes direction", link.node2h+" "+link.node2v+" nodes direction", "length", "Red", "Green", "Blue"]
    fieldValues = [link.log, link.node1direction, link.node2direction, link.length, link.red, link.green, link.blue]
    fieldValues = multenterbox(msg,title, fieldNames, fieldValues)
    if fieldValues == None:
        return False
    link.log = int(fieldValues[0])
    link.node1direction = fieldValues[1]
    link.node2direction = fieldValues[2]
    link.length = fieldValues[3]
    link.red = int(fieldValues[4])
    link.green = int(fieldValues[5])
    link.blue = int(fieldValues[6])
    return True

def editBot(bot):
    msg = "Drop Bot Box"
    title = "Edit Bot State"
    fieldNames = ["X position", "Y position", "angle (degrees)"]
    fieldValues = [bot.X, bot.Y, bot.theta]
    fieldValues = multenterbox(msg,title, fieldNames, fieldValues)
    if fieldValues == None:
        return False
    bot.X = int(fieldValues[0])
    bot.Y = int(fieldValues[1])
    bot.theta = int(fieldValues[2])
    return True
    
