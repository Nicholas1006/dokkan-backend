temp={"ABC":{"DEF":123}}
temp2=temp.copy()
del temp2["ABC"]["DEF"]
print(list(temp.keys()))