import unittest
import graph
import nodes
import math

def trunc( decimal, accuracy ):
    return int( decimal * 10 ** accuracy ) / 10 ** accuracy
def sumDistance( nodes ):
    distance = 0
    lastNode = None
    for node in nodes:
        if lastNode != None:
            distance = distance + \
                math.hypot( lastNode.X - node.X, lastNode.Y - node.Y )
        lastNode = node
    return distance

class TestNodes( unittest.TestCase ):
    def test_ExplorePath_Branches1puck( self ):
        """
        Checks to see if explorePath can find its way from a path that
         diverges and then converges onto the destination.
        """
        nodes.DEBUG = True
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        n4a = graph.Node( 5, 40 )
        n4b = graph.Node( 15, 40 )
        n5a = graph.Node( 5, 50 )
        n5b = graph.Node( 15, 50 )
        n5a.puck = 10

        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5a ) )
        roots = [n2]
        actual = nodes.explorePath( links, roots, n2 )
        nodes.DEBUG = False 
        expectedPath = [ n2, n3, n4a, n5a ]
        d = sumDistance( expectedPath )
        expected = ( expectedPath, d )
        self.assertEqual( expected[0], actual[0] )
    def test_ExplorePath_Simple( self ):
        """
        Checks to see if explorePath can find its way from one point to another.
        """
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        n7 = graph.Node( 10, 40 )
        n7.puck = 10

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n7 ) )
        roots = [n1]
        actual = nodes.explorePath( links, roots, n1 )
        d = sumDistance( [ n1, n2, n3, n7 ] )
        expected = ( [ n1, n2, n3, n7 ], d )
        self.assertEqual( expected[0], actual[0] )
        self.assertEqual( expected[1], actual[1] )
    def test_ExplorePath2( self ):
        """
        Checks to see if explorePath can find its way from a path that
         diverges and then converges onto the destination.
        """
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        n4a = graph.Node( 5, 40 )
        n4b = graph.Node( 15, 40 )
        n5a = graph.Node( 5, 50 )
        n5b = graph.Node( 15, 50 )
        n4b.puck = 10
        n5a.puck = 10

        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5a ) )
        roots = [n2]
        actual = nodes.explorePath( links, roots, n2 )
        d = sumDistance( [ n2, n3, n4b ] )
        expected = ( [ n2, n3, n4b ], d )
        self.assertEqual( expected[0], actual[0] )
        self.assertEqual( expected[1], actual[1] )
    def test_ExplorePath( self ):
        """
        Checks to see if explorePath can find its way from a path that
         diverges and then converges onto the destination.
        """
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        n4a = graph.Node( 5, 40 )
        n4b = graph.Node( 15, 40 )
        n5a = graph.Node( 5, 50 )
        n5b = graph.Node( 15, 50 )
        n6a = graph.Node( 5, 60 )
        n6b = graph.Node( 15, 60 )
        n5b.puck = 10
        n6a.puck = 10

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5a ) )
        links.append( graph.Link( n4b, n5b ) )
        links.append( graph.Link( n5a, n6a ) )
        roots = [n1]
        actual = nodes.explorePath( links, roots, n1 )
        d = sumDistance( [ n1, n2, n3, n4b, n5b ] )
        expected = ( [ n1, n2, n3, n4b, n5b ], d )
        self.assertEqual( expected[0], actual[0] )
        self.assertEqual( expected[1], actual[1] )
    def test_ExplorePath_complex( self ):
        """
        Checks to see if explorePath can find its way from a path that
         diverges and then converges onto the destination.
        """
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        n4a = graph.Node( 5, 40 )
        n4b = graph.Node( 15, 40 )
        n5a = graph.Node( 5, 50 )
        n5b = graph.Node( 15, 50 )
        n6a = graph.Node( 5, 60 )
        n6b = graph.Node( 15, 60 )
        n7 = graph.Node( 10, 70 )
        n7.puck = 10

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5a ) )
        links.append( graph.Link( n4b, n5b ) )
        links.append( graph.Link( n5a, n6a ) )
        links.append( graph.Link( n5b, n7 ) )
        links.append( graph.Link( n6a, n7 ) )
        roots = [n1]
        actual = nodes.explorePath( links, roots, n1 )
        d = sumDistance( [ n1, n2, n3, n4b, n5b, n7 ] )
        expected = ( [ n1, n2, n3, n4b, n5b, n7 ], d )
        self.assertEqual( expected[0], actual[0] )
        self.assertEqual( trunc( expected[1], 5 ), trunc( actual[1], 5 ) )
    def test_ExplorePath( self ):
        """
        Checks to see if explorePath can find its way from a path that
         diverges and then converges onto the destination.
        """
        links = []
        n2 = graph.Node( 10, 10 )
        n3 = graph.Node( 10, 30 )
        n4a = graph.Node( 60, 40 )
        n4b = graph.Node( 15, 40 )
        n5 = graph.Node( 10, 50 )
        n7 = graph.Node( 10, 70 )
        n7.puck = 10


        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5 ) )
        links.append( graph.Link( n4b, n5 ) )
        links.append( graph.Link( n5, n7 ) )
        links.append( graph.Link( n4a, n4b ) )

        roots = [n2]
        actual = nodes.explorePath( links, roots, n2 )
        d = sumDistance( [ n2, n3, n4b, n5, n7 ] )
        expected = ( [ n2, n3, n4b, n5, n7 ], d )
        self.assertEqual( expected[0], actual[0] )
        self.assertEqual( trunc( expected[1], 5 ), trunc( actual[1], 5 ) )
    def test_findLinksWithNode( self ):
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        expected = graph.Link( n1, n2 ) 

        links.append( expected )
        links.append( graph.Link( n2, n3 ) )
        actual = nodes.findLinksWithNode( links, n1 )
        self.assertEqual( 1, len( actual ) )
        self.assertIn( expected,  actual )
        

if __name__ == '__main__':
    unittest.main()
