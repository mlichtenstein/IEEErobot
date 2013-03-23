"""
Test:
 n1 = Node( 35, 45 )
 n2 = Node( 35, 46 )
 nodes.append( n1 )
 nodes.append( n2 )
 n1.links.append( Link( n2 ) )
 n2.links.append( Link( n1 ) )
 n1.links.index( n2 )
0
 n2.links.index( n1 )
0
 remove( nodes.index( n1 ) )
 n2.links.index( n1 )
ValueError
"""
class TypedList(list):
    def __init__(self, className ):
        self._className = className

    def append(self, item):
        """
        >>> l = TypedList( int )
        >>> try:
        ...     l.append( "" )
        ... except TypeError:
        ...     print "OK"
        OK
        >>> i = 1
        >>> l.append( i )
        >>> l.remove( i )
        """
        if not isinstance( item, self._className ):
            raise TypeError, "Bad arguments: Should be a " + self._className.__name__ + " type."
        super( TypedList, self ).append( item ) 
    def remove( self, item ):
        """
        >>> l = TypedList( int )
        >>> try:
        ...     l.remove( "" )
        ... except TypeError:
        ...     print "OK"
        OK
        """
        if not isinstance( item, self._className ):
            raise TypeError, "Bad arguments: Should be a " + self._className.__name__ + " type."
        super( TypedList, self ).remove( item )

class NodeList(TypedList):
    def remove( self, item ):
        """
        >>> l = TypedList( int )
        >>> try:
        ...     l.remove( "" )
        ... except TypeError:
        ...     print "OK"
        OK
        """
        if not isinstance( item, self._className ):
            raise TypeError, "Bad arguments: Should be a " + self._className.__name__ + " type."
        for link in item.links:
            for link2 in link.destination.links:
                if link2.destination == item:
                    link.destination.links.remove( link2 )
        super( NodeList, self ).remove( item )
class Node:
    def __init__( self, XPos, YPos ):
        self.pos = XY( XPos, YPos )
        self.links = TypedList( Link )

class Link:
    def __init__( self, dest ):
        self.destination = dest

class XY:
    def __init__( self, X, Y ):
        self.X = X
        self.Y = Y

nodes = NodeList( Node )

'''
for node in nodes:
    print "Node: " + node.name
        for link in node.links:
            print link.destination.name
'''

def printNodes():
    for node in nodes:
        print "Node: " + node
        for link in node.links:
            print "Link: " + link.destination
'''
print "Final::"
for node in nodes:
    print "Node: " + node.name
        for link in node.links:
            print link.destination.name
'''
