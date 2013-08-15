import socket
compname = socket.gethostname()

if compname == 'Michal-PC':
    sqlite_path = 'C:/Users/Michal/Dropbox/Python/catacombs/database.db'
elif compname == 'mikes-imac':
    sqlite_path = '/Users/club292/Dropbox/Python/catacombs/database.db'
elif compname == '6420-64-MikeN01':
    sqlite_path = 'C:/Dropbox/Python/catacombs/database.db'
