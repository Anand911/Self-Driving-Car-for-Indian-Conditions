import pickle
dispatcher={"1":"Left1","2":"Left2","3":"Left3",
                    "4":"Right1","5":"Right2","6":"Right3",
                    "8":"Backward","9":"Forward","0":"Brake"}
def dispatch(state,mode="MANUAL"):
        try:
            msg={"mode":mode,"function":dispatcher[str(state)]}
            msg=pickle.dumps(msg)
            msg=bytes(f"{len(msg):<10}","utf-8")+msg
            return msg
            
        except KeyError:
            print("Key Error!")
            return None