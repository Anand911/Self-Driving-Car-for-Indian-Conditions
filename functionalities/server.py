import socket 
import sys
#sys.path.insert(1,"C://Users//91701//OneDrive//Documents//Final Year Project//SelfDriving")
from config import HOST
class Server():
    def __init__(self,PORT=9090):
        #print("Creating Server!")'
        self.state=True
        self.HOST = HOST
        self.PORT = PORT
        self.server = socket.socket (socket.AF_INET, socket. SOCK_STREAM) 
        self.server.bind((self.HOST, self.PORT)) 
        self.server.listen(5) 
        self.communication_socket, self.address = self.server.accept() 
        print (f"Connected to {self.address}") 

    def recieve(self):
        message = self.communication_socket.recv(1024).decode('utf-8') 
        print (f"Message from client is: {message}") 
        
    def send(self,msg):
        try:
            self.communication_socket.send(msg) 
        except ConnectionError or ConnectionAbortedError or ConnectionResetError:
            self.state=False
            print("Connection closed!")

    def closeSocket(self):
        self.state=False
        self.communication_socket.close() 
        print (f"Connection with {self.address} ended!")
