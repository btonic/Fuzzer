import csv
import sqlite3

class SQLEngine(class):
	"""
	CSV format:
	table_name, attempt_id, attempted, prohibited, successful, created_at, updated_at

	"""
	def __init__(self,
				 database_path,
				 tables_to_cache=None):
		#tables_to_cache is never used, it is simply
		#for compliance with the fuzzer.
		self.database_path = database_path
		self.get_tables()
	def get_tables(self):
		"""
		Get all tables in the CSV.
		"""
		self.tables_in_csv=[]
		csv = CSVConnection(self.database_path)
		for row in csv.reader:
			if row[0] in self.tables_in_csv:
				continue
			else:
				self.tables_in_csv.append(row[0])
		csv.close()
	def create_database(self, table_name, *columns):
		"""
		Create the database if it does not exist.
		"""
		pass
		csv = CSVConnection(self.database_path)
		if table_name in self.tables_in_csv:
			raise TableAlreadyExists("`%s` already exists.")
		else:
			#strip types, not needed
			csv.write([table_name]+list(column[0] 
				                        for column in columns))
		#update tables definition
		self.get_tables()
		csv.close()
	def read_query(self, query, *args):
		"""
		"""
		pass
	def append_to_pool(self, item, table_name):
		"""
		"""
		pass
	def commit_pool(self):
		"""
		"""
		pass

class CSVConnection(class):
	def __init__(self, csv_path):
		self.csv = open(csv_path,'rw')
		self.reader = csv.reader(csv)
		self.writer = csv.writer(csv)
	def read(self):
		return self.reader.next()
	def write(self, row, *args, **kwargs):
		self.writer.write_row(row, *args, **kwargs)
	def close(self):
		self.csv.close()