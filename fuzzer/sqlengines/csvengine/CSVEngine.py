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
		csv.close()
		#update tables definition
		self.get_tables()
	def read_query(self, query, *args):
		"""
		"""
		#This is a special function. Since csv does not use sql,
		#we have to parse the sql and pull the necessary information.
		#In order to do this, a tempfile will be used for ordering
		held_results=[]
		query = query.lower().split()
		#Pull SELECT --->(values)<---... from query
		select_values = query[(query.index("select")+1):query.index("from")]
		#clean up the values
		select_values = list(value.strip() for value in select_values.split(","))
		#Pull FROM --->(table)<--- from query
		if where_clause:
			from_table = query[(query.index("from")+1):query.index("where")][0]
		else:
			from_table = query[(query.index("from")+1)]
		#pull conditions
		if where_clause and limit_clause:
			where_conditions = query[(query.index("where")+1):query.index("limit")]
			where_conditions = list(condition.split("=") for condition in where_conditions)
		elif where_clause:
			where_conditions = query[(query.index("where")+1):]
			where_conditions = list(condition.split("=") for condition in where_conditions)
		#pull order
		if limit_clause:
			order_by = query[(query.index("by")+1):query.index("limit")]
		else:
			order_by = query[(query.index("by")+1):]
		#pull limit
		if limit_clause:
			limit = query[(query.index("limit")+1):][0].split(";")[0]
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