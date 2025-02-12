import os
for root, dirs, files in os.walk("temp_jsons"):
    for file in files:
        os.remove(os.path.join(root, file))
