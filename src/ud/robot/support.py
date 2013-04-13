

def makeTimer( seconds ):
    """
    Makes a lambda function which returns true while their is time remaining.

    @param seconds is the number seconds to return true.

    @return a lambda function thats true while for number of seconds.

    Example
    >>> import time
    >>> timer = makeTimer( 0.100 )
    >>> timer()
    True
    >>> startTime = time.time()
    >>> while timer() and startTime + 0.200 > time.time():
    ...     pass
    >>> timer()
    False
    """
    import time
    startTime = time.time()
    return lambda : time.time() - startTime < seconds

if __name__=="__main__":
    import time
    timer = makeTimer( 4 )
    while timer():
        print time.time()