# ServidorHello.py

import sys, getopt
import socket

DefaultPort = 12345

def startServer(portNumber) :
    print( "Starting Hello server on port {}".format(portNumber) )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind( ("localhost", portNumber) )
        while True :
            s.listen()
            conn, addr = s.accept()
            print( "New connection ({})".format( addr ) )
            response = "Hello "
            with conn:
                while True :
                    dataAsByte = conn.recv(1)
                    
                    if not dataAsByte :
                        break

                    dataAsString = dataAsByte.decode( "utf-8" ).upper()

                    if ( dataAsString == "\r"  ) :
                        continue

                    response += dataAsString

                    if ( dataAsString == "\n" ) :
                        conn.sendall( bytes( response, "utf-8" ) )
                        conn.close()
                        break

def usage() :
    print( "ServidorHello.py [--port <server port number>]" )

def parseArguments(argv) :
    print( "Parsing arguments..." )

    try:
        opts, args = getopt.getopt(argv,"h",["help", "port="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print( err )
        sys.exit( 2 )

    for opt, arg in opts:
        if opt in ( "-h", "--help" ) :
            usage()
            sys.exit()
        
        if opt in ( "-p", "--port" ) :
            startServer( int(arg) )
            sys.exit()
    
    startServer( DefaultPort )

if __name__ == "__main__":
    parseArguments( sys.argv[1:] )
