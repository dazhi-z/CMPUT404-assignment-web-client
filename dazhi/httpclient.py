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
    #get the hostname from a given url
    def getHost(self,  url):
        data = urllib.parse.urlparse(url)
        return data.hostname
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(1)
        return None

    def get_code(self, data):
        code = data[0].split(' ')[1]
        return int(code) 

    def get_headers(self,data):
        headers = data.split("\r\n")
        return headers

    def get_body(self, data):
        body = data.split('\r\n')[-1]
        return body

    #send the request
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        return self.recvall(self.socket)
        
    #close the connection
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
            print("TimeOut")
        return buffer.decode('utf-8')


    def GET(self, url, args=None):
        #divide the url into components
        urlLine = urllib.parse.urlparse(url)
        if urlLine.port:
            urlPort = urlLine.port
        else:
            #if the port does not exists, set it as default
            urlPort = 80
        
        self.connect(self.getHost(url),urlPort)

        if urlLine.path:
            urlPath = urlLine.path
        else:
            # if there is no path, set it as '/'
            urlPath = '/'

        #the GET request
        get_message = """GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n""".format(path=urlPath,  host=self.getHost(url))

        #send the request and get the response
        urlData = self.sendall(get_message) 
        urlHeader = self.get_headers(urlData)
        code = self.get_code(urlHeader)

        self.close()

        return HTTPResponse(code,urlData)

        

        
    def POST(self, url, args=None):
        urlBody = " "
        urlLine = urllib.parse.urlparse(url)

        if urlLine.port:
            urlPort = urlLine.port
        else:
            urlPort = 80
        self.connect(socket.gethostbyname(urlLine.hostname),urlPort)

        if args != None:
            urlBody = urllib.parse.urlencode(args)
        else:
            urlBody = ""

        if urlLine.path:
            urlPath = urlLine.path
        else:
            urlPath = '/'
        
        urlLen = len(urlBody)

        self.connect(self.getHost(url), urlPort)

        #the POST request
        #the Content-Type asked to handle
        post_message = """POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length}\r\n\r\n{data}""".format(path=urlPath,  data=urlBody,  length=urlLen,  host=self.getHost(url))

        #send the request and get the response
        urlData = self.sendall(post_message)
        urlHeaders = self.get_headers(urlData)
        code = self.get_code(urlHeaders)
        body = urlHeaders[-1] #the body of the response
        
        self.close()
        return HTTPResponse(code,body)

        
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