import os
#This gives you the path to the /catacombs/catacombs folder
curr_dir = os.path.dirname(os.path.abspath(__file__))
#Go up one level and you'll find your database file
root_dir = os.path.join(curr_dir, '..')
sqlite_path = os.path.join(root_dir, 'database.db')
