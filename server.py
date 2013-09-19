import socket
import select
import sys

#host determines who can connect to server. port determines what channel to listen on
host = ''
port = 81

#variable to control "listening" loop execution
running = True
notBound = True
exit = False

#server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while notBound:
	try:
		server.bind((host,port))
		notBound = False
	except:
		print("Could not bind to port " + str(port) + ". Incrementing port number by one and retrying")
		if port == 9999:
			print("Was not able to bind to a port. Exiting\n\n")
			exit = True
			break
		port += 1
if exit:
	sys.exit(0)
print("Server established on port " + str(port))
server.listen(5)                                                            #allows for five unhandled simultaneous connection attempts
#the above lines accomplishes user story "listen for connections"

#list of current connections to the server
connections = [server]                                                      #might technically be unnecessary
#dictionary mapping user sockets to usernames
usernames = {}
#the above lines partially accomplish user story "manage connections"

def main():

	while running:
		
		try:
			read,write,excepts = select.select(connections,connections,[])      #select.select() returns three lists, one of sockets ready to be read, one of sockets ready to be written
		except:
			print("Select line exception")
		
		for s in read:                                                          #for all sockets who have something to say	
			if s == server:                                                     #if the socket is the server, that means there's a new connection
				try:
					user = server.accept()[0]                                   #accept the socket object and name it user
				except:
					print("Server connect error")
					break
					
				if user not in usernames:                                       #if the user is a new user
					try:
						usernames[user] = user.recv(1024).rstrip()                  #assume the first message they send is their username
						connections.append(user)                                        #add the socket to the connection list. helps accomplish user story "manage connections"
						sendAll(user, "", "on")										#notify other users that someone has signed on
						onlineQuery(user)											#send the new connection a list of users already online
					except:
						print("User disconnected without entering a username")
			else:                                                               #if the socket is not the server, it's a user
				try:
					information = s.recv(1024)                                  #receive the message they sent. helps accomplish user story "buffer messages in"
				except ConnectionResetError:
					print("General receive exception: Connection Reset Error Handled")
					print(str(usernames[s] + b" unexpectedly disconnected")[2:-1])
					userSignoff(s)
					break
					
				if information != b'\\':
					if information[0] != 47:
						sendAll(s, information)
					else:
						if information == b'/query':
							onlineQuery(s)
						elif information[0:4] == b'/me ':
							sendAll(s, information[4:], "me")
				else:                                                           
					userSignoff(s)

	server.close()
	print("done")
			
def sendAll(user, information, signOn = ""):
	if signOn == "on":
		information = b"has just signed on"
		middle = b" "
	elif signOn == "off":
		information = b"has just signed off"
		middle = b" "
	elif signOn == "me":
		middle = b" "
	else:
		middle = b": "
	
	print(str(usernames[user] + middle + information)[2:-1] + '\n')
	
	for c in connections:
		if c != server and c != user:
			try:
				c.send(usernames[user] + middle + information)
			except:
				print(str(b"Send error to " + usernames[c])[2:-1])
				break


def onlineQuery(user):
	online = 'Currently online: ' + ', '.join("{!s}".format(val)[2:-1] for val in usernames.values()) 
	try:
		user.send(online.encode('utf-8'))
	except:
		print(("Query error to " + usernames[user])[2:-1])
	
def userSignoff(user):
	sendAll(user, "", "off")
	del usernames[user]
	connections.remove(user)
	user.close()
			
if __name__ == '__main__':
	main()
