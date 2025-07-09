import shutil
import os

def move_to_frontend(src, dest):
    for filename in os.listdir(src):
        file_path = os.path.join(src, filename)
        if os.path.isfile(file_path):
            fileDest = os.path.join(dest, filename)
            # Create the destination directory if it doesn't exist
            os.makedirs(os.path.dirname(fileDest), exist_ok=True)
            if os.path.exists(fileDest):
                os.remove(fileDest)
            shutil.move(file_path, fileDest)
            print("Moved:", file_path)
        else:
            new_dest = os.path.join(dest, filename)
            # Create the destination directory for subdirectories
            os.makedirs(new_dest, exist_ok=True)
            move_to_frontend(file_path, new_dest)

move_to_frontend("temp_jsons", "../frontend/dbManagement/")