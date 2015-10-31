from codecs import open
import sqlite3

DB = 'db.sqlite3'
ALL_RESULTS = 'all.tsv'
GOOD_RESULTS = 'good.tsv'
TABLE = 'zh_slovo_answer_user'

def main():
	connection = sqlite3.connect(DB)
	cursor = connection.cursor()
	cursor.execute(
		'CREATE INDEX IF NOT EXISTS'
		' {table}_id_hash ON {table} (id_hash);'.format(table=TABLE))
	connection.commit()
	add_all_results(cursor, connection)
	add_good_results(cursor, connection)
	connection.close()

def add_all_results(cursor, connection):
	for id_hash, user_text, grade in table(ALL_RESULTS):
		(n,), = cursor.execute(
			'SELECT count(*) FROM {table}'
			' WHERE id_hash = ?'.format(table=TABLE), (id_hash,))
		if n == 0:
			cursor.execute(
				'INSERT INTO {table} (id_hash, user_text, grade, sex, city)'
				' VALUES (?, ?, ?, "", "")'.format(table=TABLE),
				(id_hash, user_text, grade))
	connection.commit()

def add_good_results(cursor, connection):
	for (username, age, sex, city, email, prof,
			 edu, id_hash, dict_id) in table(GOOD_RESULTS):
		cursor.execute(
			'UPDATE {table} SET username=?, age=?, sex=?, city=?,'
			' email=?, prof=?, edu=?, dict_id=?'
			' WHERE id_hash = ?'.format(table=TABLE),
			(username, age, sex, city, email, prof,
				 edu, dict_id, id_hash))
	connection.commit()

def table(filename):
	with open(filename, 'r', encoding='utf-8') as fd:
		for line in fd:
			yield line.rstrip('\n\r').split('\t')

if __name__ == "__main__":
	main()
