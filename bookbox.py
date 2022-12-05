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
    max_id = cursor.execute('''SELECT MAX(id) FROM books''').fetchone()[0]
    min_id = cursor.execute('''SELECT MIN(id) FROM books''').fetchone()[0]
    
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
            pass
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
    nlp = spacy.load('en_core_web_sm')

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
    print(suggested)
    
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
            ID:\t\t{str(tup[0])}
            TITLE:\t\t{tup[1]}
            AUTHOR:\t\t{tup[2]}
            QUNTITY:\t{str(tup[3])}""")
            

# create search function
def search():
    
    selection = ''

    while selection != '0':
        # choose how to search for a book
        selection = input(
            """Choose your search parameter: \n
            1 - select by id
            2 - select by title
            3 - select by author
            4 - show all books
            0 - exit\n""")

        if selection == '1':
            
            # get the min and max id numbers
            min_id, max_id = id_range()
            
            # print acceptable id numbers
            print(f"\nMax ID: {max_id}\n\nMin ID: {min_id}\n")

            # get selection of id from the user
            book_id = input("\nEnter the id of the book you wish to edit: \n")

            # check input within acceptable parameters
            while int(book_id) < min_id or int(book_id) > max_id:
                print("\nINPUT NOT WITHIN BOUNDS\n")
                
                # print max / min ID
                id_range()
                
                book_id = input("\nEnter the id of the book you are searching for: \n")

                if book_id == '0':
                    break

            # get the book record with the chosen id
            result = cursor.execute(
                f"""
                SELECT * FROM books WHERE id = ?""", (book_id,)).fetchone()

            # print the result of the query
            parse_record(result)

            ##########  WHAT DO I WANT TO RETURN ???? #######
            return result


        elif selection == '2':
            target_title = input("\nEnter the title of the book: \n")
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

            parse_record(result)

            ##########  WHAT DO I WANT TO RETURN ???? #######
            return result


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
            
            parse_record(result)
            
            return result
            
        elif selection == '4':
            # get list of tuples of all books in database
            all_books_tuples = cursor.execute(
                """
                SELECT * FROM books""").fetchall() # list of tuples - eg. [(name,), (next_name,),...]
            
            parse_record(all_books_tuples)


        elif selection == '0':
            print("\nExiting search\n")
        else:
            print("\n\nSelection not recognised\n")


# create INSERT INTO functionality
# increment id field (primary key) by one

# function takes the current max id as input
def add_book():
    
    # get the max id so it can be incremented by one for each new book
    # the query returns a tuple (3001,) so select the first element which is the id number (int)
    max_id = cursor.execute('''SELECT MAX(id) FROM books''').fetchone()[0]
    max_id += 1

    title = input("\nEnter the title of the book you wish to enter into the database: \n")
    author = input("\nEnter the name of the author: \n")

    try:
        qty = int(input("\nEnter the number of copies of the book we have in stock: \n"))
    except ValueError:
        print("\nENTRY FAILED\n\nRemember that the number of copies has to be an integer!\n\n")
        
        return

    # Insert book into database
    cursor.execute('''INSERT INTO books(id, title, author, qty)
                      VALUES(?,?,?,?)''', (max_id, title, author, qty))

    print('\nNew book inserted')


# function to delete book
def delete_book():
    
    # get the target id of the book to be deleted
    target = input("\nEnter the ID of the book you wish to delete: \n")
    
    cursor.execute(
    f"""
    DELETE FROM books WHERE id = ?""", (target,))
    
    # print message that book jas been successfully deleted
    
    print("DELETE SUCCESSFUL")
    

###############################################################################

# connect or create database
db = sqlite3.connect('bookbox_jupyter_db')

# initiate cursor
cursor = db.cursor()

# create database
# cursor.execute('''
#     CREATE TABLE student(id INTEGER PRIMARY KEY, name TEXT,
#                    	grade INTEGER)
# ''')
# db.commit()


######################### ADD BOOKS TO DATABASE ########################################
# id1 = 3001
# title1 = 'A Tale of Two Cities'
# author1 = 'Charles Dickens'
# qty1 = 30

# # Insert book 1
# cursor.execute('''INSERT INTO books(id, title, author, qty)
#                   VALUES(?,?,?,?)''', (id1, title1, author1, qty1))
# print('First book inserted')

# id2 = 3002
# title2 = "Harry Potter and the Philospher's Stone"
# author2 = 'J.K. Rowling'
# qty2 = 40

# # Insert book 2
# cursor.execute('''INSERT INTO books(id, title, author, qty)
#                   VALUES(?,?,?,?)''', (id2, title2, author2, qty2))
# print('Second book inserted')

# id3 = 3003
# title3 = "The Lion, the Witch and the Wardrobe"
# author3 = 'C.S. Lewis'
# qty3 = 25

# # Insert book 3
# cursor.execute('''INSERT INTO books(id, title, author, qty)
#                   VALUES(?,?,?,?)''', (id3, title3, author3, qty3))
# print('Third book inserted')

# id4 = 3004
# title4 = "The Lord of the Rings"
# author4 = 'J.J.R Tolkein'
# qty4 = 37

# # Insert book 4
# cursor.execute('''INSERT INTO books(id, title, author, qty)
#                   VALUES(?,?,?,?)''', (id4, title4, author4, qty4))
# print('Fourth book inserted')

# id5 = 3005
# title5 = "Alice in Wonderland"
# author5 = 'Lewis Carrol'
# qty5 = 12

# # Insert book 5
# cursor.execute('''INSERT INTO books(id, title, author, qty)
#                   VALUES(?,?,?,?)''', (id5, title5, author5, qty5))
# print('Fifth book inserted')

# db.commit()

########################################################################################

# main program logic
main_menu()

db.close()