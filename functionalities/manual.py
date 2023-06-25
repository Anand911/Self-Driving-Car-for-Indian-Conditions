from utils import dispatch
class ManualDriving():
    
    def __init__(self):
        #print("Manual Drive Object Created!")
        self.running=False
        self.MODE="MANUAL"
    
    
    def run(self,state,server):
        state=chr(state)
        self.running=True
        msg=dispatch(state,self.MODE)
        if msg:
            server.send(msg)
        
        
    
    def stop(self,server):
        self.running=False
        #Brake 
        server.send(dispatch(0))


        
