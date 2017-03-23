y=[]
x=[]
with open("offset.txt","r") as offsfil:
   for line in offsfil:
      data=line.split(" ")
      y.append(data[0])
      x.append(data[3])
 
