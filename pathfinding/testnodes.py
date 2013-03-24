import unittest
import graph
import nodes
import math

class TestNodes( unittest.TestCase ):
    def test_ExplorePath_Simple( self ):
        """
        Checks to see if explorePath can find its way from one point to another.
        """
        links = []
        n1 = graph.Node( 10, 10 )
        n2 = graph.Node( 10, 20 )
        n3 = graph.Node( 10, 30 )
        n7 = graph.Node( 10, 40 )
        d = 0
        d = d + math.hypot( n1.X - n2.X, n1.Y - n2.Y )
        d = d + math.hypot( n2.X - n3.X, n2.Y - n3.Y )
        d = d + math.hypot( n3.X - n7.X, n3.Y - n7.Y )

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n7 ) )
        roots = [n1]
        actual = nodes.explorePath( links, roots, n1 )
        expected = ( [ n1, n2, n3, n7 ], d )
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
        d = 0
        d = d + math.hypot( n1.X - n2.X, n1.Y - n2.Y )
        d = d + math.hypot( n2.X - n3.X, n2.Y - n3.Y )
        d = d + math.hypot( n3.X - n4b.X, n3.Y - n4b.Y )
        d = d + math.hypot( n4b.X - n5b.X, n4b.Y - n5b.Y )

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5a ) )
        links.append( graph.Link( n4b, n5b ) )
        links.append( graph.Link( n5a, n6a ) )
        roots = [n1]
        actual = nodes.explorePath( links, roots, n1 )
        expected = ( [ n1, n2, n3, n4b, n5b ], d )
        self.assertEqual( expected[0], actual[0] )
        self.assertEqual( expected[1], actual[1] )
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
        print "expected:", expected
        print "actual:", actual
        self.assertIn( expected,  actual )
        

if __name__ == '__main__':
    unittest.main()
