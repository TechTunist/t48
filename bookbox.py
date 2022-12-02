import sqlite3

# connect or create database
db = sqlite3.connect('/data/bookbox_db')

# initiate cursor
cursor = db.cursor()

# create database
cursor.execute('''
    CREATE TABLE student(id INTEGER PRIMARY KEY, name TEXT,
                   	grade INTEGER)
''')
db.commit()

# present menu to user
selection = ''

# run the menu loop until '0' selected
while selection.lower() != '0':

    # print the menu and obtain user selection
    selection = input("""
    1 - Enter Book
    2 - Update Book
    3 - Delete Book
    4 - Search Book
    0 - Exit\n""")

    if selection == '1':
        pass
    elif selection == '2':
        pass
    elif selection == '3':
        pass
    elif selection == '4':
        pass
    elif selection == '0':
        print("\n\nExiting program\n")
        break


