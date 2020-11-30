from os import system, name
from time import sleep
import datetime	
import sys
import ibm_db, ibm_db_dbi
import pandas as pd
import re

# Dsn Variables
dsn_uid = 'YOUR_USER_ID'
dsn_pwd = 'YOUR_PASSWORD'
dsn_hostname = 'dashdb-txn-sbox-yp-dal09-10.services.dal.bluemix.net'
dsn_driver = '{IBM DB2 ODBC DRIVER}'
dsn_database = 'BLUDB'
dsn_port = '50000'
dsn_protocol = 'TCPIP'

# Dsn string
dsn = (
        "DRIVER={0};"
        "DATABASE={1};"
        "HOSTNAME={2};"
        "PORT={3};"
        "PROTOCOL={4};"
        "UID={5};"
        "PWD={6};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd)

# Trying to connect
system("mode 77, 26")
try: 
	conn = ibm_db.connect(dsn, "", "")
	print('\n' * 12,"Connected to the database!".center(76))
	sleep(1)
except: 
	print('\n' * 11, "Unable to connect!".center(76))
	print("Check your connection or try again later!".center(76))
	sleep(2)
	sys.exit()

def clear():
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

def print_intro(txt, size=38):
	clear()
	print('=-'*size, end='\n\n')
	print(f"{txt}".center(size*2 - 1), end='\n\n')
	print('-='*size)

def print_credits():
	print('\n' * 5)
	print('-='*38)
	print("Thanks for using my program!".rjust(76))
	print("Follow me on GitHub: @mateusvictor".rjust(76))

def read_integer(text):
	count = 0
	while count < 2:
		try:
			integer = int(input(text))
		except:
			print("  Some error ocurred! Please try again.\n")
			count += 1
			continue
		else:
			return integer
			break
	return -1

def read_option(options, text='  ==> '): 
	count = 0
	while count < 2:
		chosen_option = read_integer(text)
		if chosen_option == -1:
			break
		if chosen_option in options:
			return chosen_option
		else:
			print(f"  Please, only numbers between {options[0]} and {options[-1]}\n")
			count += 1
			continue
		 
	return False

def current_datetime():
	current_datetime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

	return current_datetime

def is_user(user):
	where_query = f"SELECT * FROM USERS WHERE USERNAME = '{user}'"
	where_stmt = ibm_db.exec_immediate(conn, where_query)

	return ibm_db.fetch_both(where_stmt) != False

def is_email(email):
	where_query = f"SELECT * FROM USERS WHERE EMAIL = '{email}'"
	where_stmt = ibm_db.exec_immediate(conn, where_query)

	return ibm_db.fetch_both(where_stmt) != False

def new_id():
	year_month = datetime.datetime.now().strftime("%Y%m")

	max_id_query = "SELECT MAX(ID) FROM USERS"
	max_id_stmt = ibm_db.exec_immediate(conn, max_id_query)

	# Select only the 4 last characters from the max id  
	max_id = str(ibm_db.fetch_both(max_id_stmt)[0])
	max_id = str(int(max_id[7:]))

	new_id = int(f"{year_month}{max_id.zfill(6)}") + 1

	return new_id	

def check_email(email):
	regex_email = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

	if re.search(regex_email, email):
		return True
	return False

def validate_credentials(user, key='', email=''):
	invalid_chars = '\'\"´~^`;'

	if len(user) < 5 or len(user) > 100:
		return False

	# Validating email
	if email != '':
		if check_email(email) == False or len(email) > 100:
			return False

	# Validating user 
	for c in user:
		if c in invalid_chars or c == ' ':
			return False

	# Validating password
	if key != '':
		if len(key) < 4 or len(key) > 100:
			return False
		for c in key:
			if c in invalid_chars or c == ' ':
				return False

	return True

def update_last_login(user):
	update_query = f"UPDATE USERS SET LAST_LOGIN = ? WHERE USERNAME = ? OR EMAIL = ?"
	update_stmt = ibm_db.prepare(conn, update_query)

	ibm_db.bind_param(update_stmt, 1, current_datetime())
	ibm_db.bind_param(update_stmt, 2, user)
	ibm_db.bind_param	(update_stmt, 3, user)
	ibm_db.execute(update_stmt)

def login_authenticator(user, key):
	if validate_credentials(user, key) == False:
		return False

	where_query = f"SELECT * FROM USERS WHERE (USERNAME = ? OR EMAIL = ?) AND PASSWORD = ?;"
	where_stmt = ibm_db.prepare(conn, where_query)

	ibm_db.bind_param(where_stmt, 1, user)
	ibm_db.bind_param(where_stmt, 2, user)
	ibm_db.bind_param(where_stmt, 3, key)
	ibm_db.execute(where_stmt)
	
	result = ibm_db.fetch_both(where_stmt)

	if result != False:
		update_last_login(user)
		return True
	else:
		return False

def register_user(user, key, email):
	if validate_credentials(user, key, email) == False:
		return False

	if is_user(user) or is_email(email):
		return False

	insert_query = f"INSERT INTO USERS VALUES (?, ?, ?, ?, ?)"
	insert_stmt = ibm_db.prepare(conn, insert_query)

	ibm_db.bind_param(insert_stmt, 1, new_id())
	ibm_db.bind_param(insert_stmt, 2, email)
	ibm_db.bind_param(insert_stmt, 3, user)
	ibm_db.bind_param(insert_stmt, 4, key)
	ibm_db.bind_param(insert_stmt, 5, current_datetime())

	ibm_db.execute(insert_stmt)

	return True

def print_users():
	select_query = "SELECT ID, USERNAME, LAST_LOGIN FROM USERS"
	pandas_conn = ibm_db_dbi.Connection(conn)
	dataframe = (pd.read_sql(select_query, pandas_conn).to_string()).split('\n')
	print()

	for line in dataframe:
		print(f"{line}".center(99))
		
def delete_user(user):
	if validate_credentials(user) == False:
		return False
	if is_user(user) == False:
		return False

	delete_query = "DELETE FROM USERS WHERE USERNAME = ?"
	delete_stmt = ibm_db.prepare(conn, delete_query)

	ibm_db.bind_param(delete_stmt, 1, user)
	ibm_db.execute(delete_stmt)
	return True

menu = '''
	[ 1 ] - Login
  	[ 2 ] - Register a new user
  	[ 3 ] - See all users*
  	[ 4 ] - Delete a user*
  	[ 5 ] - Exit
  	* require ADM credentials
'''

while True:
	system("mode 77, 26")
	print_intro('Login System')
	print(menu)

	choice = read_option([n for n in range(1, 5 + 1)])

	if choice == False:
		continue
	
	if choice == 1:
		print_intro('[ 1 ] Login Mode')

		print('\n  Type a user and a password existent.\n')
		user_login =     str(input('  User or email:  ')).strip()
		password_login = str(input('  Password:       ')).strip()

		print_intro('[ 1 ] Login Mode')
		print('\n  Type a user and a password existent.\n')
		print(f'  User or email:  {user_login}')
		print(f'  Password:       {(len(password_login))*"*"}')

		print('\n  Verifying...\n')

		sleep(0.5)

		if login_authenticator(user_login, password_login):
			print('  Success: Congratulations! You are registered in our database!')
		else:
			print('  Erro: User or password invalid! Try again or register a new user!')
		print('\n  '*10, end='')
	
	if choice == 2:
		print_intro('[ 2 ] Register Mode')
	
		print('\n  Type a new user, email and a password.\n')

		email_register =    str(input('  Email:    ')).strip().lower()
		user_register =     str(input('  User:     ')).strip()
		password_register = str(input('  Password: ')).strip()

		print_intro('[ 2 ] Register Mode')
		print('\n  Type a new user, email and a password.\n')
		print(f'  Email:    {email_register}')
		print(f'  User:     {user_register}')
		print(f'  Password: {(len(password_register))*"*"}')

		print('\n  Registering...\n')

		sleep(0.5)

		if register_user(user_register, password_register, email_register):
				print(f"  Success: User '{user_register}' successfully registered!\n\n\n\n")
		else:
			print(f"  Erro: Invalid or in use credentials")
			print(f"  User and password must have between 5 and 100 characters.")
			print(f"  User and password can not have spaces or the characters: [' \" ´ ~ ` ^ ;]")
			print(f"\n  Try again with a new and valid username, email and password.")
		
		print('\n  '*5, end='')

	if choice == 3:
		print_intro('[ 3 ] ADM Mode')

		print('\n  Type the user and the password.\n')

		user_adm =     str(input('  User (ADM):     ')).strip()
		password_adm = str(input('  Password (ADM): ')).strip()

		print_intro('[ 3 ] ADM Mode')
		print('\n  Type the user and the password.\n')
		print(f'  User (ADM):     {user_adm}')
		print(f'  Password (ADM): {(len(password_adm))*"*"}')
		
		print('\n  Verifying...\n')
		sleep(1)

		if user_adm == dsn_uid and password_adm == dsn_pwd:
			system("mode 99, 99")
			print_intro('[ 3 ] ADM Mode', 49)
			print_users()
			print('\n  ', end='')
		else:
			print('  Access Denied!')
			print('\n  '*10, end='')

	if choice == 4:
		print_intro('[ 3 ] ADM Mode')

		print('\n  Type the user and the password.\n')

		user_adm =     str(input('  User (ADM):     ')).strip()
		password_adm = str(input('  Password (ADM): ')).strip()

		print_intro('[ 3 ] ADM Mode')
		print('\n  Type the user and the password.\n')
		print(f'  User (ADM):     {user_adm}')
		print(f'  Password (ADM): {(len(password_adm))*"*"}')
		
		print('\n  Verifying...\n')
		sleep(1)

		if user_adm == dsn_uid and password_adm == dsn_pwd:
			print_intro('[ 4 ] ADM Mode')
			print('\n  Type the username you want to delete from the database.\n')
			user_delete = str(input('  User to delete: '))

			if delete_user(user_delete):
				print(f"\n  Sucess: User '{user_delete}' deleted successfully!")
			else:
				print(f"\n  Erro: No user '{user_delete}' registered in our database!")

			print('\n  '*13, end='')
		else:
			print('  Access Denied!')
			print('\n  '*10, end='')

	if choice == 5:
		print_credits()
		ibm_db.close(conn)
		break

	system('pause')