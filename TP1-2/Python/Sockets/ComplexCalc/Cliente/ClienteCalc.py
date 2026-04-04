import socket
import json
import sys


def showResponse(r1, i1, oper, r2, i2, res_r, res_i):
    print("({} + {}i) {} ({} + {}i) = {} + {}i".format(r1, i1, oper, r2, i2, res_r, res_i))

def main():
    host = 'localhost'
    port = 12349

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    print("Connecting to {} at port {}".format(host, port))
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            
            r1, i1 = 5, 2
            r2, i2 = 3, 4

            operations = []
            operations.append({"r1": r1, "i1": i1, "r2": r2, "i2": i2, "oper": "+"})
            operations.append({"r1": r1, "i1": i1, "r2": r2, "i2": i2, "oper": "-"})
            operations.append({"r1": r1, "i1": i1, "r2": r2, "i2": i2, "oper": "*"})

            request = {"operations": operations}
            requestJSON = json.dumps(request)
            
            s.sendall(bytes(requestJSON, "utf-8"))

            responseRaw = s.recv(4096).decode("utf-8")
            response = json.loads(responseRaw)
            results = response.get("results", [])

            if len(results) >= 3:
                showResponse(r1, i1, '+', r2, i2, results[0]["rRes"], results[0]["iRes"])
                showResponse(r1, i1, '-', r2, i2, results[1]["rRes"], results[1]["iRes"])
                showResponse(r1, i1, '*', r2, i2, results[2]["rRes"], results[2]["iRes"])
            
        except Exception as e:
            print("Error:", e)

    print("Client ending.")

if __name__ == "__main__":
    main()
