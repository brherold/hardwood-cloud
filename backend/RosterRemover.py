#For Updating the Roster, this script will clear out the folders that contain the old data.

'''
Folders to Clear:
- TeamRosterPage
'''


from send2trash import send2trash
import os

year = 2055

if year == 2055:

    folders = ['TeamRosterPage']

    for folder in folders:
        if os.path.isdir(f"backend/{folder}"):
            for filename in os.listdir(f"backend/{folder}"):
                #print(filename)
                if f'-{year}' in filename:
                    #print(filename)
                    filepath = os.path.join(f"backend/{folder}", filename)
                    send2trash(filepath)
                    print(f"Trashed: {filepath}")