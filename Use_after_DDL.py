import time
start_time = time.time()
#print("+-----------------------------------+")
#exec(open("Convert Files (use JP).py").read())

#activate if global first and available on dokkaninfo.com
exec(open("Database expander.py").read())
print("+-----------------------------------+")
exec(open("Convert Files.py").read())
print("+-----------------------------------+")
exec(open("dokkan Json creator.py").read())
print("+-----------------------------------+")
exec(open("uniqueJsonCreator.py").read())
print("+-----------------------------------+")
print("Program completed in", round(time.time()-start_time,2), "seconds")
#medium_time=time.time()
#exec(open("Create true mosaic wallpaper.py").read())
#print("+-----------------------------------+")
#print("True mosaic completed in", round(time.time()-medium_time,2),"seconds")