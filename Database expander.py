from progress.bar import Bar
import sqlite3 as sl
import pandas as pd


GLOBAL_DB_LOC = "Dokkan Asset Downloader\DokkanFiles\global\en\sqlite\current\en\database.db"

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