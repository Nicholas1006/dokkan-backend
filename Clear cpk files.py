import os

for root, _, files in os.walk("C:/Users/horva/OneDrive - Trinity College Dublin/Documents/dokkan/frontend/dbManagement/DokkanFiles"):
    for file in files:
        # Check if the file ends with .cpk
        if file.endswith('.cpk'):
            # Construct the full path to the file
            file_path = os.path.join(root, file)
            try:
                # Remove the file
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except OSError as e:
                print(f"Error removing {file_path}: {e}")
