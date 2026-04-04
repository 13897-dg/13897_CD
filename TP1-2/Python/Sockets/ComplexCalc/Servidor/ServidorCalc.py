# ServidorCalc.py

import getopt
import socket
import json
import sys
from threading import Thread

DefaultPort = 12349

DebugMessages = False

def ServidorDedicado(cliConnection, cliAddress):
    print("Starting thread to handle data from {}".format(cliAddress))

    global DebugMessages

    with cliConnection:
        while True:
            try:
                requestRaw = cliConnection.recv(4096).decode("utf-8")
                
                # If no data received, client cleanly closed connection
                if not requestRaw:
                    break

                request = json.loads(requestRaw)
                
                if DebugMessages:
                    print("Request received:\n{}".format(request))

                operations = request.get("operations", [])
                
                results = []
                for op in operations:
                    r1 = op.get("r1")
                    i1 = op.get("i1")
                    r2 = op.get("r2")
                    i2 = op.get("i2")
                    oper = op.get("oper")

                    match oper:
                        case '+':
                            rRes = r1 + r2
                            iRes = i1 + i2
                        case '-':
                            rRes = r1 - r2
                            iRes = i1 - i2
                        case '*':
                            rRes = (r1 * r2) - (i1 * i2)
                            iRes = (r1 * i2) + (i1 * r2)
                        case _:
                            print("Invalid operation")
                            rRes = 0
                            iRes = 0

                    if DebugMessages:
                        print(" ({} + {}i) {} ({} + {}i) = {} + {}i".format(r1, i1, oper, r2, i2, rRes, iRes))

                    results.append({"rRes": rRes, "iRes": iRes})

                response = {"results": results}
                responseJSON = json.dumps(response)
                
                if DebugMessages:
                    print("Response to send in JSON:\n{}".format(responseJSON))

                cliConnection.sendall(bytes(responseJSON, "utf-8"))
            except socket.error as sockEx:
                print("Socket error!\nDetails:\n{}".format(sockEx))
                break

            except json.JSONDecodeError as jsonEx:
                print("JSON Decode error!\nDetails:\n{}".format(jsonEx))
                break

            except Exception as genEx:
                print("Generic error!\nDetails:\n{}".format(genEx))
                break

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
