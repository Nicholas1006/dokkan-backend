import shutil
import os


def move_to_frontend(src, dest):
    for filename in os.listdir(src):
        file_path = os.path.join(src, filename)
        if os.path.isfile(file_path):
            fileDest = os.path.join(dest,filename)
            if os.path.exists(fileDest):
                os.remove(fileDest)
            shutil.move(file_path, fileDest)
            print("Moved:",file_path)
        else:
            move_to_frontend(file_path, os.path.join(dest, filename))


src="temp_jsons"
dest="../frontend/dbManagement/"

move_to_frontend(src, dest)