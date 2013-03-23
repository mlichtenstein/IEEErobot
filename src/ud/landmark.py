
class landmark:
    x,y = 0,0 #in feet, of course
    def __init__(self, x, y):
        """
        Create a landmark  at x feet, y feet of type rock() or tree()
        """
        self.x,self.y = (x,y)
    def getXY(self):
        return self.x,self.y
    def undraw(self, boardCanvas):
        try:
            boardCanvas.delete(self.id)
        except:
            print "Delete failed (maybe it never existed?)"

class tree(landmark):
    """
    Examples
    >>> isinstance( tree(1,2), landmark)
    True
    >>> isinstance( tree(1,2), tree)
    True
    """
    treeSide = 3.5/12
    color = (0x8B, 0x69, 0x14)
    def draw(self, boardCanvas):
        x,y = getXY()*boardCanvas.width/8
        s=self.treeSide*boardCanvas.width/8/2
        self.id = boardCanvas.create_rectange(x-s, y-s, x+s, y+s, fill=color)

class rock(landmark):
    rockRadius = 6.7/12/2
    color = (0x7F,0x7F, 0x7F)
    def draw(self, boardCanvas):
        x,y = getXY()*boardCanvas.width/8
        s=self.rockRadius*boardCanvas.width/8/2
        self.id = boardCanvas.create_oval(x-s, y-s, x+s, y+s, fill=color)
