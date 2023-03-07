import sqlite3
import os



def create_new_db(new_db_path):

	con = sqlite3.connect(new_db_path)



def create_table_in_db(db_path, table_name, table_columns:dict):

	if os.path.exists(db_path):
		con = sqlite3.connect(db_path)
		cur = con.cursor()

		table_query = "CREATE TABLE IF NOT EXISTS " + table_name
		table_query += ' (id INTEGER PRIMARY KEY AUTOINCREMENT, '
		
		for column_name, column_param in table_columns.items():
			table_query += f'{column_name} {column_param}, '
		
		table_query = list(table_query)[:-2]
		table_query = ''.join(table_query)
		table_query += ")"
		print(table_query)

		cur.execute(table_query)

		print('Tabela dodana poprawnie!')
	
	else:
		print('Podana baza danych nie istnieje')



def add_data(datas:dict, table_name, db_path):

	if os.path.exists(db_path):
		con = sqlite3.connect(db_path)
		cur = con.cursor()
	
		query = f'INSERT INTO {table_name} '
		query += '(' + ','.join([x for x in datas.keys()]) + ') VALUES' + '('
		query += ','.join(['?' for _ in datas.values()])
		query += ')'
	
		print(query)
		values = list(datas.values())
		cur.execute(query, values)
		con.commit()
		print('Dodano informację do bazy danych!')

	else:
		print('Baza danych nie istnieje.')



def get_data(what:list, db_path, table_name):
	
	con = sqlite3.connect(db_path)
	cur = con.cursor()

	if what:
		what_command = ','.join(what)
	
	else:
		what_command = '*'

	get_query = f'SELECT {what_command} FROM {table_name}'

	print(get_query)
	
	result = cur.execute(get_query)
	result = result.fetchall()

	return result



def clear_table(db_path, table_name):

	con = sqlite3.connect(db_path)
	cur = con.cursor()

	cur.execute(f'DELETE FROM {table_name};')
	#reset id autoincrement
	cur.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
	con.commit()
	con.close()

	print('Baza danych wyczyszczona. Usunięto ', cur.rowcount, 'pozycji w bazie danych!')

if __name__ == '__main__':

	table_columns = {
		'name': 'TEXT', 
		'email':'TEXT', 
		'password':'TEXT',
	}

	table_data = {
		'name': 'vf4321431g', 
		'email':'r4314321re@gmail.com', 
		'password':'432143214213o',
	}


	db_path = (os.getcwd() + '/db_folder/' + 'users' + '.db')
	#add_data(table_data, 'users', db_path)
	#print(get_data(['password'], db_path,'users'))
	
	#get_data([],{},'AND',1,'users', db_path)
	#clear_table(db_path, 'users')
	#create_new_db(new_db_path)
	# db_name = input('Wprowadź nazwę bazy danych: ')
	# table_name = input('Wprowadź nazwę tabeli: ')
	# create_table_in_db(db_path, table_name, table_columns)
	