import os
for root, dirs, files in os.walk("temp_jsons"):
    for file in files:
        os.remove(os.path.join(root, file))

for root, dirs, files in os.walk("Dokkan_Asset_downloader/temp_downloads"):
    for file in files:
        if file != "database.db":
            os.remove(os.path.join(root, file))
for root, dirs, files in os.walk("Dokkan_Asset_downloader/temp_downloads"):
    for dir in dirs:
        if not os.listdir(os.path.join(root, dir)):
            os.rmdir(os.path.join(root, dir))

