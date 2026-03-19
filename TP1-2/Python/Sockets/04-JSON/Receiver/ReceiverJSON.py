# ReceiverJSON.py

#https://docs.python.org/3/library/struct.html

import sys, getopt
import socket

from threading import Thread
import struct

import json

DefaultPort = 12350

DebugMessages = False

def ServidorDedicado(cliConnection, cliAddress):
    print( "Starting thread to handle data from {}".format(cliAddress) )

    global DebugMessages

    with cliConnection:
        while True :
            try :
                requestRaw = cliConnection.recv( 1024 ).decode( "utf-8" )
                print( "Resquest in raw format:\n{}".format( requestRaw ) )

                request = json.loads( requestRaw )
                print( "\nResquest:\n{}".format( request ) )

                items = request.get( "items" )
                print( "\nItems:\n{}".format( items ) )

                accTemperature = 0.0
                for currentItem in request.get( "items" ) :
                    print( "\nCurrent MyItem: {}".format( currentItem ) )

                    print( "\nCurrent Timestamp: {}".format( currentItem.get( "timestamp" ) ) )
                    print( "\nCurrent Temperature: {}".format( currentItem.get( "temperature" ) ) )

                    accTemperature = accTemperature + currentItem.get( "temperature" )
                
                avgTemperature = accTemperature / len( request.get( "items" ) )

                response = { "Temperature average" : avgTemperature }

                print( "\nResponse to send:\n{}".format( response ) )

                responseJSON = json.dumps( response )
                print( "\nResponse to send in JSON:\n{}".format( responseJSON ) )

                cliConnection.sendall( bytes( responseJSON, "utf-8" ) )

            except socket.error as sockEx :
                print( "Socket error!\nDetails:\n{}".format( sockEx ) )
                break

            except Exception as genEx :
                print( "Generic error!\nDetails:\n{}".format( genEx ) )
                continue
        
        cliConnection.close()

        print( "Thread to handle data from {} is ending".format(cliAddress) )

def usage() :
    print( "ReceiverJSON.py [--port <server port number>]" )

def startServer(portNumber) :
    print( "Starting JSON server reader on port {}".format(portNumber) )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind( ( "localhost" , portNumber ) )
        while True :
            s.listen()
            conn, addr = s.accept()
            
            print( "New connection ({})".format( addr ) )

            tt = Thread( target=ServidorDedicado, args=(conn, addr,) )
            tt.start()

def parseArguments(argv) :
    print( "Parsing arguments..." )

    try:
        opts, args = getopt.getopt(argv, "h", [ "debug", "help", "port=" ])
    except getopt.GetoptError as err:
        # print help information and exit:
        print( err )
        sys.exit( 2 )

    hostPort = DefaultPort

    for opt, arg in opts:
        if opt in ( "-h", "--help" ) :
            usage()
            sys.exit()
        
        if opt in ( "--port" ) :
            hostPort = int(arg)
        
        if opt in ( "--debug" ) :
            print( "Debug messages active." )
            global DebugMessages
            DebugMessages = True
    
    startServer( hostPort )

if __name__ == "__main__":
    parseArguments( sys.argv[1:] )
