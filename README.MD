# AWS MySQL Library

This repository contains the `AWSMySQLLib` class, which provides a convenient interface to interact with a MySQL database hosted on AWS RDS. The class includes methods for connecting to the database, executing queries, and managing database objects.

## Features

- Initialize the connection using configuration from a file.
- Test connectivity to the AWS RDS host.
- Connect to the AWS RDS MySQL instance and specific databases.
- Retrieve information about databases and tables.
- Create and remove databases and tables.
- Insert, update, delete, and list records in tables.
- Manage database connections efficiently.
- Pytest integration for testing all functionalities.

## Requirements

- Python 3.7+
- `pymysql` library
- `configparser` library
- `socket` library
- `pytest` library
- `logging` library

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/aws-mysql-lib.git
   ```

2. Install the required packages:

   ```sh
   pip install pymysql
   ```

3. Ensure you have a `logging_storageservice.cfg` configuration file for logging.

## Usage

### Initialization

You can initialize the `AWSMySQLLib` class either directly by providing the connection details or through a configuration file.

#### Direct Initialization

```python
from awsmysqllib import AWSMySQLLib

aws_db = AWSMySQLLib(host='your-host', user='your-username', password='your-password', database='your-database', port=3306)
```

Initialization from a Configuration File
Create a configuration file awsmysql.cfg with the following format:

```
[AWS_MYSQL_CONFIG]
host = your-host
user = your-username
password = your-password
database = your-database
port = 3306
```

Then, initialize the class:

```
from awsmysqllib import AWSMySQLLib

aws_db = AWSMySQLLib.init_from_file('awsmysql.cfg')
```

Methods

- test_can_reach_host(): Test if the AWS RDS host is reachable.
- connect_to_rds_host(): Connect to the AWS RDS MySQL instance.
- connect_to_database(): Connect to the specified database.
- get_database_info(): Retrieve detailed information about databases.
- get_database_properties(database_name: str): Retrieve properties of a database.
- check_database_exists(database_name: str): Check if a database exists.
- create_database(database_name: str): Create a database.
- remove_database(database_name: str): Remove a database.
- create_table(table_name: str, columns: Dict[str, str]): Create a table with the specified columns.
- list_tables_with_columns(): List all tables within the database with details about their columns.
- delete_table(table_name: str): Delete a table.
- list_entries_in_table(table: str): List all entries within a specified table.
- insert_record(table: str, data: Dict[str, Union[str, int, float]]): Insert a record into the specified table.
- update_record(table: str, record_id: int, data: Dict[str, Union[str, int, float]]): Update a record in the specified table.
- delete_record(table: str, record_id: int): Delete a record from the specified table.
- close_connection(): Close the connection to the MySQL database.

### Example

```
from awsmysqllib import AWSMySQLLib

# Initialize the AWSMySQLLib instance
aws_db = AWSMySQLLib.init_from_file('awsmysql.cfg')

# Test if the host is reachable
if aws_db.test_can_reach_host():
    print("Host is reachable")

# Connect to the database
if aws_db.connect_to_database():
    print("Connected to the database")

# List tables with their columns
tables_info = aws_db.list_tables_with_columns()
print(tables_info)

# Insert a record into a table
record_id = aws_db.insert_record('example_table', {'name': 'John Doe', 'age': 30})
print(f"Inserted record ID: {record_id}")

# Close the connection
aws_db.close_connection()
```

## Testing

This project includes pytest tests to ensure the library functions as expected. The tests are located in the _tests_ directory and cover all major functionalities of the library.

To run the tests, use:

```
pytest -sv test_aws_db_connection.py
```

## Logging

This library uses Python's built-in logging module. Make sure you have a logging configuration file (logging_storageservice.cfg) set up to capture the logs.
