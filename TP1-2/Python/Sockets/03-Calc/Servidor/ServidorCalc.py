# ServidorCalc.py

# https://docs.python.org/3/library/struct.html

import getopt
import socket
import struct
import sys
from threading import Thread

DefaultPort = 12349

DebugMessages = False

"""
    Ler um valor inteiro (4 bytes) no formato Litle Endian (processadores Intel)
"""


def readIntV1(connection):
    val = 0
    i = 0
    while i < 4:
        aux = connection.recv(1)[0]
        val = (aux << (i * 8)) | val
        i = i + 1

    return val


"""
    Ler um valor inteiro (4 bytes) no formato Big Endian / Network (processadores Motorola / Java) - v1
"""


def readIntV2(connection):
    val = 0
    i = 3
    while i >= 0:
        aux = connection.recv(1)[0]
        val = (aux << (i * 8)) | val
        i = i - 1

    return val


"""
    Ler um valor inteiro (4 bytes) no formato Big Endian / Network (processadores Motorola / Java) - v2
"""


def readIntV3(connection):
    return struct.unpack("!i", connection.recv(4))[0]


"""
    Ler um valor inteiro (4 bytes)
"""


def readInt(connection):
    # return readIntV1(connection)
    return readIntV2(connection)
    # return readIntV3(connection)


"""
    Escrever um valor inteiro no formato nativo.
    
    Corresponde ao hardware onde o servidor se está a executar 
"""


def writeIntV1(connection, value):
    connection.sendall(struct.pack('@i', value))


"""
    Escrever um valor inteiro no formato Litle Endian (processadores Intel)
"""


def writeIntV2(connection, value):
    mask = 0x000000ff
    i = 0
    while i < 4:
        aux = (value & (mask << (i * 8))) >> (i * 8)

        if DebugMessages:
            print("Sending {}".format(aux))

        connection.sendall(struct.pack('b', aux))
        i = i + 1


"""
    Escrever um valor inteiro no formato Big Endian (processadores Motorola)
"""


def writeIntV3(connection, value):
    mask = 0xff000000
    i = 3
    while i >= 0:
        aux = (value & (mask >> (3 - i) * 8)) >> (i * 8)

        if DebugMessages:
            print("Sending {}".format(aux))

        connection.sendall(struct.pack('b', aux))
        i = i - 1


"""
    Escrever um valor inteiro (4 bytes) do formato local para network (Big Endian) 
"""


def writeIntV4(connection, value):
    aux = struct.pack("!i", value)

    if DebugMessages:
        print("Sending {}".format(aux))

    connection.sendall(aux)


"""
    Escrever um valor inteiro
"""


def writeInt(connection, value):
    # writeIntV1(connection, value)
    # writeIntV2(connection, value)
    writeIntV3(connection, value)
    # writeIntV4(connection, value)


def readByte(connection):
    return connection.recv(1).decode("utf-8")


def ServidorDedicado(cliConnection, cliAddress):
    print("Starting thread to handle data from {}".format(cliAddress))

    global DebugMessages

    with cliConnection:
        while True:
            try:
                op1 = readInt(cliConnection)
                op2 = readInt(cliConnection)
                oper = readByte(cliConnection)

                match oper:
                    case '+':
                        res = op1 + op2
                    case '-':
                        res = op1 - op2
                    case '*':
                        res = op1 * op2
                    case '/':
                        res = round(op1 / op2)
                    case _:
                        print("Invalid operation")
                        break

                if DebugMessages:
                    print(" {} ({:0x}) {} {} ({:0x}) = {} ({:0x})".format(op1, op1, oper, op2, op2, res, res))
                    print("Going to send: {}".format(res))

                writeInt(cliConnection, res)
            except socket.error as sockEx:
                print("Socket error!\nDetails:\n{}".format(sockEx))
                break

            except struct.error as strEx:
                print("Unpack error!\nDetails:\n{}".format(strEx))
                break

            except IndexError as idxEx:
                print("No more data to read!\nDetails:\n{}".format(idxEx))
                break

            except Exception as genEx:
                print("Generic error!\nDetails:\n{}".format(genEx))
                continue

        cliConnection.close()

        print("Thread to handle data from {} is ending".format(cliAddress))


def usage():
    print("ServidorCalc.py [--port <server port number>]")


def startServer(portNumber):
    print("Starting Calc server on port {}".format(portNumber))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", portNumber))
        while True:
            s.listen()
            conn, addr = s.accept()

            print("New connection ({})".format(addr))

            tt = Thread(target=ServidorDedicado, args=(conn, addr,))
            tt.start()


def parseArguments(argv):
    print("Parsing arguments...")

    try:
        opts, args = getopt.getopt(argv, "h", ["debug", "help", "port="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        sys.exit(2)

    hostPort = DefaultPort

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

        if opt in "--port":
            hostPort = int(arg)

        if opt in "--debug":
            print("Debug messages active.")
            global DebugMessages
            DebugMessages = True

    startServer(hostPort)


if __name__ == "__main__":
    parseArguments(sys.argv[1:])
