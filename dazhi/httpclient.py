#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host(self,url):
        host = urllib.parse.urlparse(url).hostname
        return host

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(1)
        return None

    def get_code(self, data):
        status_code = data[0].split(' ')[1]
        return int(status_code)

    def get_headers(self,data):
        headers = data.split("\r\n")
        return headers

    def get_body(self, data):
        body = data.split("\r\n")[-1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        try:
            while not done:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
        except socket.timeout:
            print("timeout")
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        #parse the given url
        parse_url = urllib.parse.urlparse(url)

        if parse_url.port:
            port = parse_url.port
        else:
            #if the port does not exist, set it as default
            port= 80
        
        self.connect(self.get_host(url),port)

        if parse_url.path:
            url_path = parse_url.path
        else:
            #if there is no path, set the path as '/'
            url_path = '/'

        #the GET request
        get_request = """GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n""".format(path=url_path,  host=self.get_host(url))

        #send the request and get the response
        self.sendall(get_request)
        body = self.recvall(self.socket)
        headers = self.get_headers(body)
        status_code = self.get_code(headers)

        #close the connection
        self.close()

        return HTTPResponse(status_code, body)

    def POST(self, url, args=None):
        parse_url = urllib.parse.urlparse(url)

        if parse_url.port:
            url_port = parse_url.port
        else:
            url_port = 80
        
        self.connect(self.get_host(url),url_port)

        if parse_url.path:
            url_path = parse_url.path
        else:
            url_path = '/'

        #encode args in url format
        if args != None:
            url_body = urllib.parse.urlencode(args)
        else:
            url_body = ""

        

        #the POST request
        #Content-Type asked to handle
        post_request = """POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length}\r\n\r\n{data}""".format(path=url_path,  data=url_body,  length=len(url_body),  host=self.get_host(url))

        self.sendall(post_request)
        data = self.recvall(self.socket)
        headers = self.get_headers(data)
        status_code = self.get_code(headers)
        body = headers[-1]

        self.close()
        
        return HTTPResponse(status_code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))