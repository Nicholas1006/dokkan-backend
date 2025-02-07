from progress.bar import Bar
import sqlite3 as sl
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the backend repo directory
DOWNLOAD_DIR = os.path.join(BASE_DIR, "Dokkan_Asset_Downloader")  # Path to store new files
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "temp_downloads")  # Path to store new files
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "global")  # Path to store new files
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "en")  # Path to store new files
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "sqlite")  # Path to store new files
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "current")  # Path to store new files
DOWNLOAD_DIR = os.path.join(DOWNLOAD_DIR, "en")  # Path to store new files
GLOBAL_DB_LOC = os.path.join(DOWNLOAD_DIR, "database.db")  # Path to store new files



bar = Bar('Expanding global database file', max=219)
con = sl.connect(GLOBAL_DB_LOC)
with con:
    x = con.execute("""SELECT name FROM sqlite_master
WHERE type='table'
ORDER BY name;""")
    for title in x:
        title=title[0]
        mylist = "SELECT * FROM " + title + ";"
        y = con.execute(mylist)

        #Fetch column names
        columns = [description[0] for description in y.description]
        filtered_columns = [col for col in columns if col not in ["updated_at", "created_at"]]

        
        # Fetch data
        transferringdata = [
            [entry for idx, entry in enumerate(row) if columns[idx] in filtered_columns]
            for row in y
        ]

        
        
        # Create DataFrame with proper column names
        df = pd.DataFrame(transferringdata, columns=filtered_columns)
        
        fulltitle="dataGB/"+title+".csv"
        df.to_csv(fulltitle, index=False)
        bar.next()
    bar.finish()

print("Database file expanded")