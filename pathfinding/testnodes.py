import unittest
import graph
import nodes

class TestNodes( unittest.TestCase ):
    def test_ExplorePath_Simple( self ):
        """
        Checks to see if explorePath can find its way from one point to another.
        """
        links = []
        n1 = graph.Node( 10, 50 )
        n2 = graph.Node( 10, 50 )
        n3 = graph.Node( 10, 50 )
        n7 = graph.Node( 10, 50 )

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n7 ) )
        roots = [n1]
        actual = nodes.explorePath( links, roots, n1 )
        expected = [ n1, n2, n3, n7 ]
        self.assertEqual( expected, actual )
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
        n7 = graph.Node( 10, 70 )

        links.append( graph.Link( n1, n2 ) )
        links.append( graph.Link( n2, n3 ) )
        links.append( graph.Link( n3, n4a ) )
        links.append( graph.Link( n3, n4b ) )
        links.append( graph.Link( n4a, n5a ) )
        links.append( graph.Link( n4b, n5b ) )
        links.append( graph.Link( n5a, n6a ) )
        links.append( graph.Link( n6a, n7 ) )
        links.append( graph.Link( n5b, n7 ) )
        roots = [n1]
        actual = nodes.explorePath( links, n1, n1 )
        expected = [ n1, n2, n3, n4b, n5b, n7 ]
        self.assertEqual( expected, actual )
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
