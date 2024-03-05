from typing import Dict, Union, List
import pymysql
import configparser
import socket
import logging
import logging.config
logging.config.fileConfig('logging_storageservice.cfg')


class AWSMySQLLib:
    def __init__(self, host: str, user: str, password: str, database: str, port: int):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(
            f"Creating an instance of {str(self.__class__.__name__)}")
        self.logger.info("Initializing AWSMySQLLib")

    @classmethod
    def init_from_file(cls, file_name: str) -> Union[None, 'AWSMySQLLib']:
        config = configparser.ConfigParser()
        config.read(file_name)
        try:
            details = config['AWS_MYSQL_CONFIG']
            host = details['host']
            user = details['user']
            password = details['password']
            database = details['database']
            port = int(details['port'])
            return cls(host, user, password, database, port)
        except configparser.NoOptionError as err:
            cls.logger.exception("configparser.NoOptionError:")
            cls.logger.exception(err)
            return None

    def test_can_reach_host(self) -> bool:
        rds_host = self.host
        port = self.port
        self.logger.debug(
            f"Attempting to reach AWS RDS host: {rds_host}:{port}")
        try:
            with socket.create_connection((rds_host, port), timeout=5):
                pass
            self.logger.info(f"Can reach AWS RDS host: {rds_host}:{port}")
            return True
        except Exception as e:
            self.logger.exception(
                f"Failed to reach AWS RDS host: {rds_host}:{port}, Error: {e}")
            return False

    def connect_to_rds_host(self) -> bool:
        rds_host = self.host
        port = self.port
        self.logger.debug(
            f"Attempting to reach AWS RDS host: {rds_host}:{port}")
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.logger.debug(f"Connected to AWS RDS host: {rds_host}:{port}")
            version_info = self.connection.get_server_info()
            self.logger.debug(
                f"Connected to AWS MySQL RDS (version {version_info})")
            return True
        except Exception as e:
            self.logger.exception(
                f"Error connecting to AWS RDS host: {rds_host}:{port}, Error: {e}")
            return False

    def connect_to_database(self) -> bool:
        rds_host = self.host
        database = self.database
        port = self.port
        self.logger.debug(
            f"Attempting to reach database: {database}")
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.logger.debug(f"Connected to the database: {database}")
            version_info = self.connection.get_server_info()
            self.logger.debug(
                f"Connected to AWS MySQL RDS (version {version_info})")
            return True
        except Exception as e:
            self.logger.exception(f"Error connecting to the database: {e}")
            return False

    def get_database_info(self) -> list:
        """Retrieve detailed information about databases."""
        databases_info = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                result = cursor.fetchall()
                self.logger.debug("List of databases:")
                for db_name in [item[0] for item in result]:
                    self.logger.debug(f"Name: {db_name}")
                    db_info = self.get_database_properties(db_name)
                    databases_info.append(db_info)
                return databases_info
        except Exception as e:
            self.logger.exception(f"Error fetching database information: {e}")
            return None

    def get_database_properties(self, database_name: str) -> Dict[str, str]:
        """Retrieve properties of a database."""
        db_info = {}
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SHOW CREATE DATABASE `{database_name}`")
                result = cursor.fetchone()
                if result:
                    # Updated line for debugging
                    self.logger.debug("Result: %s", result)
                    # Parse the result to extract database properties
                    create_statement = result[1]
                    owner_start = create_statement.find(
                        "CREATE DATABASE") + len("CREATE DATABASE")
                    owner_end = create_statement.find("CHARACTER SET") if create_statement.find(
                        "CHARACTER SET") != -1 else len(create_statement)
                    owner = create_statement[owner_start:owner_end].strip()
                    collation_start = create_statement.find("COLLATE") + len(
                        "COLLATE") if create_statement.find("COLLATE") != -1 else len(create_statement)
                    collation_end = len(create_statement)
                    collation = create_statement[collation_start:collation_end].strip(
                    )
                    db_info['Owner'] = owner
                    db_info['Collation'] = collation
        except Exception as e:
            self.logger.exception("Error fetching database properties: %s", e)
        return db_info

    def check_database_exists(self, database_name: str) -> bool:
        """Check if a database exists."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
                result = cursor.fetchone()
                return result is not None
        except AttributeError as e:
            self.logger.exception(
                "No Connection in checking if database exists: %s", e)
            return False
        except Exception as e:
            self.logger.exception("Error checking if database exists: %s", e)
            return False

    def create_database(self, database_name: str) -> bool:
        """Create a database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE `{database_name}`")
            self.logger.info(
                f"Database '{database_name}' created successfully.")
            return True
        except Exception as e:
            self.logger.exception(
                f"Error creating database '{database_name}': {e}")
            return False

    def remove_database(self, database_name: str) -> bool:
        """Remove a database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE `{database_name}`")
            self.logger.info(
                f"Database '{database_name}' removed successfully.")
            return True
        except Exception as e:
            self.logger.exception(
                f"Error removing database '{database_name}': {e}")
            return False

    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Create a table with the specified name and columns.

        Args:
            table_name (str): The name of the table.
            columns (Dict[str, str]): A dictionary specifying column names and their data types.

        Returns:
            bool: True if the table creation is successful, False otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                column_definitions = ', '.join(
                    f"{name} {data_type}" for name, data_type in columns.items())
                query = f"CREATE TABLE {table_name} ({column_definitions})"
                cursor.execute(query)
            self.connection.commit()
            self.logger.info(f"Table '{table_name}' created successfully.")
            return True
        except Exception as e:
            self.logger.exception(f"Error creating table '{table_name}': {e}")
            return False

    def list_tables_with_columns(self) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
        """
        List all tables within the database with details about their columns.

        Returns:
            List[Dict[str, Union[str, List[Dict[str, str]]]]]: A list of dictionaries containing table information.
        """
        table_info_list = []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]

                for table_name in tables:
                    table_info = {'table_name': table_name, 'columns': []}

                    # Retrieve column information for the current table
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns_info = cursor.fetchall()

                    for column_info in columns_info:
                        column_details = {
                            'column_name': column_info[0],
                            'data_type': column_info[1],
                            'nullable': 'YES' if column_info[2] == 'YES' else 'NO',
                            'key': column_info[3],
                            'default': column_info[4],
                            'extra': column_info[5]
                        }

                        table_info['columns'].append(column_details)

                    table_info_list.append(table_info)

            self.logger.info("List of tables with column details:")
            for table_info in table_info_list:
                self.logger.info(f"Table: {table_info['table_name']}")
                for column_info in table_info['columns']:
                    self.logger.info(f"  Column: {column_info}")

            return table_info_list

        except Exception as e:
            self.logger.exception(
                f"Error listing tables with column details: {e}")
            return []

    def delete_table(self, table_name: str) -> bool:
        """
        Delete a table with the specified name.

        Args:
            table_name (str): The name of the table to delete.

        Returns:
            bool: True if the table deletion is successful, False otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                query = f"DROP TABLE IF EXISTS {table_name}"
                cursor.execute(query)
            self.connection.commit()
            self.logger.info(f"Table '{table_name}' deleted successfully.")
            return True
        except Exception as e:
            self.logger.exception(f"Error deleting table '{table_name}': {e}")
            return False

    def list_entries_in_table(self, table: str) -> Union[List[Dict[str, Union[str, int, float]]], None]:
        """
        List all entries within a specified table.

        Args:
            table (str): The name of the table.

        Returns:
            Union[List[Dict[str, Union[str, int, float]]], None]: A list of entries if successful, None otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table}")
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                entries = []
                for row in result:
                    entry = dict(zip(columns, row))
                    entries.append(entry)

                self.logger.info(f"Entries in table '{table}':")
                for entry in entries:
                    self.logger.info(entry)

                return entries

        except Exception as e:
            self.logger.exception(
                f"Error listing entries in table '{table}': {e}")
            return None

    def insert_record(self, table: str, data: Dict[str, Union[str, int, float]]) -> int:
        """
        Insert a record into the specified table.

        Args:
            table (str): The name of the table.
            data (dict): A dictionary containing the column names and values for the new record.

        Returns:
            int: The ID of the inserted record if successful, -1 otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                columns = ', '.join(data.keys())
                values = ', '.join(f"'{value}'" for value in data.values())
                query = f"INSERT INTO {table} ({columns}) VALUES ({values})"
                cursor.execute(query)
                self.connection.commit()
                record_id = cursor.lastrowid
                self.logger.info(
                    f"Record inserted successfully. Record ID: {record_id}")
                return record_id
        except Exception as e:
            self.logger.exception(f"Error inserting record: {e}")
            return -1

    def update_record(self, table: str, record_id: int, data: Dict[str, Union[str, int, float]]) -> bool:
        """
        Update a record in the specified table.

        Args:
            table (str): The name of the table.
            record_id (int): The ID of the record to update.
            data (dict): A dictionary containing the column names and new values for the record.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                updates = ', '.join(
                    f"{key} = '{value}'" for key, value in data.items())
                query = f"UPDATE {table} SET {updates} WHERE id = {record_id}"
                cursor.execute(query)
            self.connection.commit()
            self.logger.info("Record updated successfully.")
            return True
        except Exception as e:
            self.logger.exception(f"Error updating record: {e}")
            return False

    def delete_record(self, table: str, record_id: int) -> bool:
        """
        Delete a record from the specified table.

        Args:
            table (str): The name of the table.
            record_id (int): The ID of the record to delete.

        Returns:
            bool: True if the deletion is successful, False otherwise.
        """
        try:
            with self.connection.cursor() as cursor:
                query = f"DELETE FROM {table} WHERE id = {record_id}"
                cursor.execute(query)
            self.connection.commit()
            self.logger.info("Record deleted successfully.")
            return True
        except Exception as e:
            self.logger.exception(f"Error deleting record: {e}")
            return False

    def close_connection(self) -> bool:
        if self.connection and self.connection.open:
            self.connection.close()
            self.logger.debug("Connection closed.")
            return True
        else:
            return False


if __name__ == "__main__":
    print("Executing awsmysqllib.py __name__")
    aws_database = AWSMySQLLib.init_from_file('awsmysql.cfg')
