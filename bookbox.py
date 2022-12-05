"""Database Management System for Bookstore

- Implements CRUD functionality
- Utilises NLP to provide search characteristics for database entries.
- see requirements.txt for dependencies"""


import sqlite3 # database
import spacy # NLP for processing user input and comparing against database

# connect or create database
db = sqlite3.connect('bookbox_jupyter_db')

# initiate cursor
cursor = db.cursor()


############ define functions ##################

# get the min and max id's to let user know bounds of search
def id_range():
    # get the max id so it can be incremented by one for each new book
    min_id = cursor.execute('''SELECT MIN(id) FROM books''').fetchone()[0]
    max_id = cursor.execute('''SELECT MAX(id) FROM books''').fetchone()[0]
    
    return min_id, max_id


# main menu function
def main_menu():
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
            add_book()
            
        elif selection == '2':
            update_book()

        elif selection == '3':
         delete_book()

        elif selection == '4':
            search()

        elif selection == '0':
            print("\n\nExiting program\n")
            break


# helper function to use NLP to predict intended search result
# EXAMPLE query = cursor.execute("""SELECT title FROM books""").fetchall()
def predict(query_result, search_term):
    
    # initiate the language model as nlp
    nlp = spacy.load('en_core_web_md')

    # create a list of titles
    query_list = [i[0] for i in query_result]

    # create a dictionary to store titles and scores as key / value pairs
    score = {}

    # prepare user book_title to compare to returned titles
    model_search_term = nlp(search_term)

    # loop through all titles and return the most similar
    for term in query_list:
        similarity = nlp(term).similarity(model_search_term)
        # print(title + " ", similarity)

        # add the title and its similarity score to dictionary
        score[term] = similarity

    # return the title with the highest similarity score to pass to the SQL query
    suggested = max(score, key=score.get)
    print(f"Search returning results for: {suggested}")
    
    return suggested


# helper function to format database queries that return entire records in this format - (id, title, author, quantity)
def parse_record(tuple_record):
    
    # check if tuple_record is a tuple or a list of tuples
    if (type(tuple_record) == tuple):
        
        print(f"""
        ID:\t\t{str(tuple_record[0])}
        TITLE:\t\t{tuple_record[1]}
        AUTHOR:\t\t{tuple_record[2]}
        QUNTITY:\t{str(tuple_record[3])}""")
        
    # tuple_record is a list of tuples    
    else:
        for tup in tuple_record:
            print(f"""
            ID:\t\t\t{str(tup[0])}
            TITLE:\t\t{tup[1]}
            AUTHOR:\t\t{tup[2]}
            QUNTITY:\t\t{str(tup[3])}""")
            

# create search function
def search():
    
    selection = ''

    while selection != '0':
        # choose how to search for a book
        selection = input(
            """\nChoose your search parameter: \n
            1 - select by id
            2 - select by title
            3 - select by author
            4 - show all books
            0 - exit to main menu\n""")

        if selection == '1':
            
            # get the min and max id numbers
            min_id, max_id = id_range()
            
            # print acceptable id numbers
            print(f"\nMin ID: {min_id}\n\nMax ID: {max_id}\n")

            # ensure user enters an integer for id
            while True:
                try:
                    # get selection of id from the user
                    book_id = int(input("\nEnter the id of the book you are searching for, or '0' for main menu: \n"))

                    if book_id == 0:
                        return
                except ValueError:
                    print(f"\nYou have to enter an integer\n")
                    continue
                else:
                    # main menu if 0 selected
                    if book_id == '0':
                        return

                    # check input within acceptable parameters
                    while int(book_id) < min_id or int(book_id) > max_id:
                        print("\nINPUT NOT WITHIN BOUNDS\n")
                        
                        # print acceptable id numbers
                        print(f"\nMin ID: {min_id}\n\nMax ID: {max_id}\n")
                        
                        book_id = input("\nEnter the id of the book you are searching for, or '0' for main menu: \n")

                        if book_id == '0':
                            return

                    # get the book record with the chosen id
                    result = cursor.execute(
                        f"""
                        SELECT * FROM books WHERE id = ?""", (book_id,)).fetchone()

                    # print the result of the query in nice formatting
                    parse_record(result)

        # search by title search
        elif selection == '2':
            target_title = input("\nSearch by the title of the book: \n")
            # use NLP to check similarity between a book title given by user and book titles in the database

            # get list of tuples of all titles in database
            all_titles_tuples = cursor.execute(
                """
                SELECT title FROM books""").fetchall() # list of tuples - [(name,), (next_name,),...]

            # call the predict helper function
            suggested = predict(all_titles_tuples, target_title)

            # make query and store the result
            result = cursor.execute(
                f"""
                SELECT * FROM books WHERE title = ?""", (suggested,)).fetchone()

            # print the result in nice formatting
            parse_record(result)

        # search by author name
        elif selection == '3':
            target_author = input("\nEnter the name of the author: \n")

            # get list of tuples of all titles in database
            all_authors_tuples = cursor.execute(
                """
                SELECT author FROM books""").fetchall() # list of tuples - eg. [(name,), (next_name,),...]

            # call the predict function
            suggested = predict(all_authors_tuples, target_author)

            # query all books by the predicted author
            result = cursor.execute(
                f"""
                SELECT * FROM books WHERE author = ?""", (suggested,)).fetchall()
            
            # print result in nice formatting
            parse_record(result)
            
            
        elif selection == '4':
            # get list of tuples of all books in database
            all_books_tuples = cursor.execute(
                """
                SELECT * FROM books""").fetchall() # list of tuples - eg. [(name,), (next_name,),...]
            
            # print all books in nice formatting
            parse_record(all_books_tuples)

        # exit search menu
        elif selection == '0':
            print("\nExiting search\n")
        
        # print error message if selection not acceptable
        else:
            print("\n\nSelection not recognised\n")


# function to add a new book into database
def add_book():
    
    # get the max id so it can be incremented by one for each new book
    # the query returns a tuple (3001,) so select the first element which is the id number (int)
    max_id = cursor.execute('''SELECT MAX(id) FROM books''').fetchone()[0]
    max_id += 1

    title = ''
    author = ''
    # deal with null entries
    while title == '':
        title = input("\nEnter the title of the book you wish to enter into the database. It cannot be left blank: (type 0 for main menu) \n")

        # exit to main menu
        if title == '0':
            return

    while author == '':
        author = input("\nEnter the name of the author. It cannot be left blank: (type 0 for main menu)\n")
        if author == '0':
            return

    # check entry is integer
    while True:
        try:
            qty = int(input("\nEnter the number of copies of the book we have in stock: \n"))
        except ValueError:
            print("\nENTRY FAILED\n\nRemember that the number of copies has to be an integer!\n\n")
            continue
        else:
                # Insert book into database
            cursor.execute('''INSERT INTO books(id, title, author, qty)
                            VALUES(?,?,?,?)''', (max_id, title, author, qty))

            print('\nNew book inserted')
            break
    
    # save changes to database
    db.commit()


# function to delete book by specific id number
def delete_book():

    # get min and max id
    min_id, max_id = id_range()
    
    # prompt user for input while until integer provided
    while True:
        try:
            # get the target id of the book to be deleted
            target = int(input("\nEnter the ID of the book you wish to delete, or '0' for main menu: \n"))

            # exit to main menu if '0' input
            if target == 0:
                return
        except ValueError:
            print("\nINPUT NOT RECOGNISED\n\nPlease enter an integer\n")
            continue
        else:
            # if a record exists with target ID
            if target < min_id or target > max_id:
                print(f"\nThe selected ID {target} does not exist in the database")
                continue

            else:
                # user to confirm correct record selected
                # show the selected record to user for comfirmation
                parse_record(
                    cursor.execute(
                    f"""
                    SELECT * FROM books WHERE id = ?""", (target,)))

                # user confirm correct record selected
                confirm = input("\nIs this the record you wish to delete?\nType 'yes' to make confirm, 'no' to change the ID number, or 0 to exit: \n")

                # exit to main menu
                if confirm == '0':
                    return

                elif confirm.lower() == 'yes':
                    # execute the delete query
                    cursor.execute(
                    f"""
                    DELETE FROM books WHERE id = ?""", (target,))
                    
                    # check book as been deleted
                    check_delete = cursor.execute(
                    f"""
                    SELECT id FROM books WHERE id = ?""", (target,)).fetchone()

                    if check_delete == None:
                        # print message that book jas been successfully deleted
                        print("DELETE SUCCESSFUL")
                        # save changes to database
                        db.commit()
                    else:
                        print("\nSomething has gone wrong, check the database to check.\n")
            
                elif confirm.lower() == 'no':
                    continue
            break
    

# function to update title, author or quantity
def update_book():

    # get the min and max id numbers
    min, max = id_range()

    # prompt user for id number of book until acceptable input received
    while True:
        try:
            # get the target id of the book to be deleted
            target = int(input("\nEnter the ID of the book you wish to update, or '0' for main menu: \n"))
        except ValueError:
            print("\nINPUT NOT RECOGNISED\n\nPlease enter an integer\n")
            continue

        # exit to main menu
        if target == 0:
            return

        # check input is between min and max ID numbers in database
        elif target > max or target < min:
            print("\nID NOT FOUND IN DATABASE\n")
            continue

        # execute update
        else:
            # show the selected record to user for comfirmation
            parse_record(
                cursor.execute(
                f"""
                SELECT * FROM books WHERE id = ?""", (target,)))

            # user confirm correct record selected
            confirm = input("\nIs this the record you wish to update?\nType 'yes' to make changes, 'no' to change the ID number, or 0 to exit: \n")

            # exit loop
            if confirm == '0':
                break

            # execute update query
            elif confirm.lower() == 'yes':

                # ask user to confirm which field to update
                selection = input(
                """\nChoose the field to update: \n
                1 - title
                2 - author
                3 - quantity\n""")

                # update title
                if selection == '1':
                    new_title = input("\nEnter the new tile: \n")
                    # execute the update query at the target id
                    cursor.execute(
                    f"""
                    UPDATE books
                    SET title = ?
                    WHERE id = ?""", (new_title, target))
                    db.commit()
                    return

                # update author
                elif selection == '2':
                    new_author = input("\nEnter new author: \n")
                    # execute the update query at the target id
                    cursor.execute(
                    f"""
                    UPDATE books
                    SET author = ?
                    WHERE id = ?""", (new_author, target))
                    db.commit()
                    return

                # update quantity
                elif selection == '3':

                    # prompt user for int until acceptable input received
                    while True:
                        try:
                            # get the target id of the book to be deleted
                            new_quantity = int(input("\nEnter the new quantity: \n"))
                        except ValueError:
                            print("\nINPUT NOT RECOGNISED\n\nPlease enter an integer\n")
                            continue
                        else:
                            # execute the update query at the target id
                            cursor.execute(
                            f"""
                            UPDATE books
                            SET qty = ?
                            WHERE id = ?""", (new_quantity, target))
                            db.commit()
                        return

            elif confirm.lower() == 'no':
                continue
            else:
                print("\nINPUT NOT RECOGNISED\n")
                continue
        

###############################################################################

# connect or create database
db = sqlite3.connect('ebookstore')

# initiate cursor
cursor = db.cursor()

# catch database already exists error
try:
    # create database
    cursor.execute('''
        CREATE TABLE books(id INTEGER PRIMARY KEY, title CHAR(30), author CHAR(30),
                    qty INTEGER(5))
    ''')
    db.commit()
except sqlite3.OperationalError:
    print("\nThe Database for the task already exists\n")


######################### ADD BOOKS TO DATABASE ########################################
# catch sqlite3 integrity error

try:
    id1 = 3001
    title1 = 'A Tale of Two Cities'
    author1 = 'Charles Dickens'
    qty1 = 30

    # Insert book 1
    cursor.execute('''INSERT INTO books(id, title, author, qty)
                    VALUES(?,?,?,?)''', (id1, title1, author1, qty1))
    print('First book inserted')

    id2 = 3002
    title2 = "Harry Potter and the Philospher's Stone"
    author2 = 'J.K. Rowling'
    qty2 = 40

    # Insert book 2
    cursor.execute('''INSERT INTO books(id, title, author, qty)
                    VALUES(?,?,?,?)''', (id2, title2, author2, qty2))
    print('Second book inserted')

    id3 = 3003
    title3 = "The Lion, the Witch and the Wardrobe"
    author3 = 'C.S. Lewis'
    qty3 = 25

    # Insert book 3
    cursor.execute('''INSERT INTO books(id, title, author, qty)
                    VALUES(?,?,?,?)''', (id3, title3, author3, qty3))
    print('Third book inserted')

    id4 = 3004
    title4 = "The Lord of the Rings"
    author4 = 'J.J.R Tolkein'
    qty4 = 37

    # Insert book 4
    cursor.execute('''INSERT INTO books(id, title, author, qty)
                    VALUES(?,?,?,?)''', (id4, title4, author4, qty4))
    print('Fourth book inserted')

    id5 = 3005
    title5 = "Alice in Wonderland"
    author5 = 'Lewis Carrol'
    qty5 = 12

    # Insert book 5
    cursor.execute('''INSERT INTO books(id, title, author, qty)
                    VALUES(?,?,?,?)''', (id5, title5, author5, qty5))
    print('Fifth book inserted')

    db.commit()

except sqlite3.IntegrityError:
    print("\nThe database is already populated with the initial books in the task\n")

########################################################################################

# main program loop
main_menu()

db.close()