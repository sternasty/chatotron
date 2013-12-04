#First I need to create a socket object and connect it to the server
#Then I need to take user input and send that to the server
#Then I need to allow this connection to take in data from the server and
#print it to the screen

import socket
import threading
import sys

#create a socket object
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host = 'localhost'
#host = input("Input host to connect to: ")

port = 8885
#port = int(input("Input port to connect on: "))

class Send(threading.Thread):
	def run(self):
		runningSend = True
		while runningSend:
			user_input = input()
			s.send(user_input.encode('utf-8'))
			if user_input == '\\':
				runningSend = False

def connect():

        #connect socket to remote address (server) 
        try:
                connectionFail = False
                s.connect((host, port))
        except:
                print("Connection to server refused")
                connectionFail = True
	
        if connectionFail:
                sys.exit()
        else:
                print("Connected")

def send():
        
        sender = Send()
        sender.start()

def receive():
        
        runningRecv = True
        while runningRecv:
                data = s.recv(1024)
                if data == b'\\':
                        runningRecv = False
                        close()
                else:
                        print(str(data)[2:-1])

def close():
        s.close()
        print("See ya later")

def Main():
        connect()
        send()
        receive()
        
