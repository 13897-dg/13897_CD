# ClienteHello.py

import sys, getopt
import socket

DefaultHostName = "localhost"

DefaultPort = 12345

DefaultArgument = "Computacao Distribuida - Python"

def startClient(hostName, portNumber, arg) :
    print( "Starting client for {} at port {}".format(hostName, portNumber) )

    with socket.socket( socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect( ( hostName, portNumber) )
        s.sendall( bytes( arg + "\n", "utf-8" ) )
        data = s.recv(1024).decode( "utf-8" )
        print( data )
        s.close()

def usage() :
    print( "ClienteHello.py [--port <server port number>] [--name <server name>] [--arg <msg to send>]" )

def parseArguments(argv) :
    print( "Parsing arguments..." )

    try:
        opts, args = getopt.getopt(argv, "h", ["name=", "port=", "arg="] )
    except getopt.GetoptError as err:
        # print help information and exit:
        print( err )
        sys.exit( 2 )

    hostPort = DefaultPort
    hostName = DefaultHostName
    argument = DefaultArgument

    for opt, arg in opts:
        if opt in ( "-h", "--help" ) :
            usage()
            sys.exit()

        if opt in ( "--name" ) :
            hostName = arg        
        elif opt in ( "--port" ) :
            hostPort = int(arg)
        elif opt in ( "--arg" ) :
            argument = arg
        else :
            assert False, "unhandled option"

    startClient( hostName, hostPort, argument )

if __name__ == "__main__":
    parseArguments( sys.argv[1:] )
