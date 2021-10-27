from http.server import BaseHTTPRequestHandler, HTTPServer
from base64 import b64encode, b64decode
import json
import sys
import getopt

d, n = 0, 0

HEADER_ERROR = {'message': b64encode('Header Error'.encode('ascii')).decode('ascii')}
JSON_DECODE_ERROR = {'message': b64encode('Json Decode Error'.encode('ascii')).decode('ascii')}
KEY_ERROR = {'message': b64encode('Key Error'.encode('ascii')).decode('ascii')}
ENC_ERROR = {'message': b64encode('Encoding/Encryption Error'.encode('ascii')).decode('ascii')}


def int_to_bytes(n):
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')


def bytes_to_int(bytes):
    return int.from_bytes(bytes, 'big')


def ceil_div(a, b):
    return (a + b - 1) // b


def base64_to_int(base64_string):
    base64_bytes = base64_string.encode('ascii')
    bytes = b64decode(base64_bytes)
    return bytes_to_int(bytes)


def int_to_base64(n):
    bytes = int_to_bytes(n)
    base64_bytes = b64encode(bytes)
    return base64_bytes.decode('ascii')


def decrypt(int_cipher):
    int_plain = pow(int_cipher, d, n)
    return int_to_bytes(int_plain)


def oracle(base64_cipher):
    int_cipher = base64_to_int(base64_cipher)
    plain = decrypt(int_cipher)
    plain = (b'\x00' * (ceil_div(n.bit_length(), 8) - len(plain))) + plain
    oracle_result = 'True' if  plain[:2] == b'\x00\x02' else 'False'
    return b64encode(oracle_result.encode('ascii')).decode('ascii')


class A3Server(BaseHTTPRequestHandler):

    def _send_response(self, json_message, code):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Accept', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(json_message), 'utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = f"<html><head></head><body><h1>You're all set!</h1></body></html>"
        self.wfile.write(bytes(html, "utf8"))

    def do_POST(self):
        headers = self.headers
        if headers['Content-Type'] != 'application/json':
            self._send_response(HEADER_ERROR, 400)
        if headers['Accept'] != 'application/json':
            self._send_response(HEADER_ERROR, 400)
        try:
            body = self.rfile.read((int(headers['Content-Length'])))
            request = json.loads(body)
            base64_cipher = request['message']
            oracle_result = oracle(base64_cipher)
            self._send_response({'message': oracle_result}, 200)
        except json.JSONDecodeError:
            self._send_response(JSON_DECODE_ERROR, 400)
        except KeyError:
            self._send_response(KEY_ERROR, 400)
        except:
            self._send_response(ENC_ERROR, 400)


def main(argv):
    global d, n
    try:
        opts, args = getopt.getopt(argv, "hd:n:")
    except getopt.GetoptError:
        print('server.py -d [path to decryption_key.txt] -n [path to modulus.txt]')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('usage: server.py -d [path to decryption_key.txt] -n [path to modulus.txt]')
            sys.exit(0)
        elif opt == '-d':
            try:
                f = open(arg, 'r')
                d = f.read()[:-1]
                d = base64_to_int(d)
            except:
                print('File Error')
                sys.exit(1)
        elif opt == '-n':
            try:
                f = open(arg, 'r')
                n = f.read()[:-1]
                n = base64_to_int(n)
                # print(n)
            except:
                print('File Error')
                sys.exit(1)
    if n == 0 or d == 0:
        print('usage: server.py -d [path to decryption_key.txt] -n [path to modulus.txt]')
        sys.exit(1)
    httpd = HTTPServer(('localhost', 8080), A3Server)
    httpd.serve_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
