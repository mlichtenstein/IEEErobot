import settings

class Messenger:
    """
    Messenger objects are used to send and recieve messages to the
    lower deck (ie the Arduino).

    Class Tests:
    """
    def __init__( self, serialWrapper ):
        """
        # Should not accept anything but SerialPort classes.
        >>> try:
        ...     instance = Messenger( "" )
        ... except TypeError:
        ...     print "OK"
        OK
        """
        if __debug__ and not isinstance( serialWrapper, SerialPort ):
            raise TypeError, "Should be a \"SerialPort\" type."
        self.__responseHandler = 0
        self.__buffer = ""
        self.__inBox = []
        self.__inMessage = False
        self.__serialWrapper = serialWrapper
        self.__message = ""
        if not self.__serialWrapper.makeContact():
            raise Exception( "Could not make contact." )
    def setResponseHandler( self, stateObject ):
        """
        Examples
        # Should not accept anything but SerialPort classes.
        >>> try:
        ...     instance = Messenger.setResponseHandler( "", "" )
        ... except TypeError:
        ...     print "OK"
        OK
        """
        if __debug__ and not isinstance( stateObject, Mode ):
            raise TypeError, "Should be a \"Mode\" type."
        self.__responseHandler = stateObject
    def sendMessage( self, charCategory, *fields ):
        """
        Sends a message to the Arduino layer which is composed
         of a category and the fields.
        
        Post Conditions:
            Message has been sent.
        
        Params:
            charCategory -- a single character which helps the Arduino
                understand the message.
            fields -- a list of additional parameters passed. Each param
                must be able to converted to a string.
                Enter this argument as a list of comma separated values:
                messenger.sendMessage(SERVICE_SCAN,1,3,MattsBalls)
        Throws:
            TypeError -- when charCategory is not a string.
            Exception -- when the length of charCategory is not 1.
        Examples:
        # Should not accept anything but strings.
        >>> try:
        ...     instance = Messenger.sendMessage( "", 1 )
        ... except TypeError:
        ...     print "OK"
        OK
        >>> try:
        ...     instance = Messenger.sendMessage( "", "ab" )
        ... except Exception:
        ...     print "OK"
        OK
        """
        if __debug__:
            if not isinstance( charCategory, str ):
                raise TypeError, "Should be a \"str\" type."
            if len( charCategory ) != 1:
                raise Exception, "Cannot be longer than one character."
            for field in fields:
                str( field )
        id = 1
        self.__serialWrapper.write( ":" )
        self.__serialWrapper.write( charCategory )
        self.__serialWrapper.write( id )
        for field in fields:
            self.__serialWrapper.write( ',' )
            self.__serialWrapper.write( str( field ) )
        self.__serialWrapper.write( ";" )
    def checkInBox( self ):
        """
        Reads the bytes coming into the serial port while the buffer
         is full.
        
        Returns:
            True -- when a full message is received.
            False -- when no message is found yet.
        """
        while True:
            # Read input and received chars.
            byte = self.__serialWrapper.read()
            if byte == False:
                return False
            else:
                if byte == ':':
                    self.__inMessage = True
                elif byte == ';':
                    self.__inMessage = False
                    if len( self.__buffer ) > 0:
                        self.__message = self.__buffer
                        self.__buffer = ""
                        return True
                elif self.__inMessage:
                    self.__buffer = self.__buffer + byte
    def getMessage( self ):
        """
        Accesses the stored message. Accessing the message
         will clear the stored message.
        
        Post Conditions:
            Stored message is cleared.
        
        Returns:
            False -- if there is no message stored.
            String -- the message stored.
        """
        if len( self.__message ) == 0:
            print("message of zero length")
            return False
        ret = self.__message
        self.__message = ""
        #import copy
        return ret
        #copy.copy( self.__message )
    def getMessageTuple(self):
        string = self.getMessage()
        print("Arduino says: " + string)
        tup = string.split(",", 3)
        return tup

class SerialPort:
    """
    Isolates the Python serial library of choose from other components of the 
        brain and provides easier testing.

    Preconditions:
    >>> import serial
    >>> import settings
    """
    import settings
    def __enter__( self ):
        return self

    def __exit__( self, type, value, traceback ):
        """
        Deconstructor. Called automatically with the "with" statement.

        Example:
        >>> import serial
        >>> try:
        ...     with SerialPort() as t:
        ...         pass
        ... except serial.SerialException:
        ...     raise Exception( "This example requires an arduino" \
                 " plugged in and the correct port address." )
        """
        if not isinstance(value, TypeError):
            self.__ser.close()

    def __init__( self, port = settings.SERIAL_PORT_ADDRESS ):
        """
        Initializes the class by setting local variables and opening the port.

        Throws:
            SerialException -- When the port fails to open.

        Examples:
        >>> import serial
        >>> try:
        ...     SerialPort( port = "/dev/fooBar" )
        ... except serial.SerialException as e:
        ...     print "OK"
        OK
        >>> try:
        ...     with SerialPort() as instanceOfSerialPort:
        ...         pass
        ... except serial.SerialException:
        ...     raise Exception( "This example requires" \
                 " an arduino plugged in and the correct port address." )
        """
        import serial
        import settings
        import time
		#the following section is for Max's computer.
		#increments through port names until it finds an available one
        
        i = 0
        done = False
        self.port = "/dev/ttyACM"
        while not done:
            tempPort = self.port + str(i)
            print("trying to connect to " + tempPort + "...")
            try:
                self.__ser = serial.Serial( 
                    port = tempPort, baudrate = settings.SERIAL_PORT_SPEED )
                self.connected = True
                self.port = tempPort
                print("Yes! Connected to "+tempPort)
                done = True
            except serial.SerialException as e:
                print("...Nope!  ",e)
                i += 1
            if i > 30:
                print("no serial today, guy")
                done = True
                raise Exception("Either you have 30 serial connections\
						or something else is wrong")
        
        # Avoid race condition
        time.sleep(1)
        # Wait 100 ms while reading.
        self.__ser.timeout = 0.1

    def makeContact( self, timeout = settings.SERIAL_PORT_SESSION_TIMEOUT ):
        """
        Makes contact with the Arduino chip. After a certain time, the method
         failes.

        Parameters:
            timeout -- How long to wait before failing.

        Returns:
            True -- If contact was made sucessfully.
            False -- If contact failed.

        Examples:
        >>> import serial
        >>> try:
        ...     with SerialPort() as instance:
        ...         instance.makeContact()
        ... except serial.SerialException:
        ...     raise Exception( "This example requires" \
                 " an arduino plugged in and the correct port address." )
        True
        """
        import support
        import settings
        sessionTimer = support.makeTimer( timeout )
        pcByte = settings.SERIAL_PORT_HELLO_BYTE
        byte = 0
        while byte != settings.SERIAL_PORT_HELLO_BYTE:
            if not sessionTimer():
                return False
            self.__ser.write( settings.SERIAL_PORT_HELLO_BYTE )
            #print( "PC says: " + pcByte )
            byte = self.__ser.read()
            #print( "Arduino says: " + byte )
        # Clear extra input and output in the buffers.
        self.__ser.flushInput()
        self.__ser.flushOutput()
        return True

    def readAndWait( self ):
        """
        Reads a byte if there is one waiting in the buffer.

        Returns:
            The byte -- If one is availiable.
            False -- If the buffer is empty.

        Examples:
        >>> import serial
        >>> try:
        ...     with SerialPort() as instance:
        ...         instance.read()
        ... except serial.SerialException as e:
        ...     raise Exception( "This example requires" \
                 " an arduino plugged in and the correct port address." )
        """
        return __ser.read()

    def read( self ):
        """
        Reads a byte if there is one waiting in the buffer.

        Returns:
            The byte -- If one is availiable.
            False -- If the buffer is empty.

        Examples:
        >>> import serial
        >>> try:
        ...     with SerialPort() as instance:
        ...         instance.read()
        ... except serial.SerialException as e:
        ...     raise Exception( "This example requires" \
                 " an arduino plugged in and the correct port address." )
        """
        if self.__ser.inWaiting() > 0:
            return self.__ser.read()
        else:
            return False

    def close( self ):
        """
        Closes the serial port connection.

        Examples:
        >>> import serial
        >>> try:
        ...     connection = SerialPort()
        ... except:
        ...     raise Exception( "This example requires" \
                 " an arduino plugged in and the correct port address." )
        ... else:
        ...     connection.close()
        """
        self.__ser.close()

    def write( self, serializable ):
        """
        Writes a object that can be converted to a string to the serial port.
        Examples:
        >>> import serial
        >>> try:
        ...     with SerialPort() as instance:
        ...         instance.write( 'a' )
        ... except serial.SerialException:
        ...     raise Exception( "This example requires" \
                 " an arduino plugged in and the correct port address." )
        """
        self.__ser.write( str( serializable ) )

if __name__=="__main__":
    import time
    print("hello world")
    with SerialPort() as serialPort:
        messenger = Messenger( serialPort )
        # Request the scan.
        messenger.sendMessage( settings.ROBOT_PING_TEST )
        #avoid race condition
        time.sleep(0.5)
        # Check for messages. Pass any messages to the mode.
        if messenger.checkInBox():
            print( messenger.getMessageTuple() )
