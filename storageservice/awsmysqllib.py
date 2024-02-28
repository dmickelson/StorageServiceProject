import pymysql
import configparser
import socket
import logging
import logging.config
logging.config.fileConfig('logging_storageservice.cfg')


class AWSMySQLLib:
    def __init__(self, host, user, password, database, port):
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
    def init_from_file(cls, file_name: str):
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

    def test_can_reach_host(self):
        rds_host = self.host
        port = self.port
        try:
            with socket.create_connection((rds_host, port), timeout=5):
                pass
            self.logger.info(f"Can reach AWS RDS host: {rds_host}")
        except Exception as e:
            self.logger.exception(
                f"Failed to reach AWS RDS host: {rds_host}, Error: {e}")

    def connect_to_database(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.logger.debug("Connected to the database.")
        except Exception as e:
            self.logger.debug(f"Error connecting to the database: {e}")

    def get_database_info(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                result = cursor.fetchall()
                databases = [item[0] for item in result]
                print("List of databases:")
                for db in databases:
                    self.logger.info(f"Name: {db}")
        except Exception as e:
            self.logger.exception(f"Error fetching database information: {e}")

    def get_database_properties(self, database_name):
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

    def check_database_exists(self, database_name):
        """Check if a database exists."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            self.logger.exception("Error checking if database exists: %s", e)
            return False

    def create_database(self, database_name):
        """Create a database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE `{database_name}`")
            self.logger.info(
                f"Database '{database_name}' created successfully.")
        except Exception as e:
            self.logger.exception(
                f"Error creating database '{database_name}': {e}")

    def remove_database(self, database_name):
        """Remove a database."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE `{database_name}`")
            self.logger.info(
                f"Database '{database_name}' removed successfully.")
        except Exception as e:
            self.logger.exception(
                f"Error removing database '{database_name}': {e}")

    def close_connection(self):
        if self.connection and self.connection.open:
            self.connection.close()
            self.logger.debug("Connection closed.")


if __name__ == "__main__":
    print("Executing awsmysqllib.py __name__")
    aws_database = AWSMySQLLib.init_from_file('awsmysql.cfg')
