import pytest
from storageservice import awsmysqllib

# ? pytest -sv test_aws_db_connection.py


TABLE_NAME = 'example_table'
AWS_RDS_CONFIG_FILE = './awsmysql.cfg'  # Change to your actual file path


@pytest.fixture
def aws_database():
    aws_db = awsmysqllib.AWSMySQLLib.init_from_file(AWS_RDS_CONFIG_FILE)
    aws_db.connect_to_database()
    yield aws_db
    aws_db.close_connection()


@pytest.fixture
def aws_rds_host():
    aws_db = awsmysqllib.AWSMySQLLib.init_from_file(AWS_RDS_CONFIG_FILE)
    aws_db.connect_to_rds_host()
    yield aws_db
    aws_db.close_connection()


# ? pytest -sv test_aws_db_connection.py::test_can_reach_host
def test_can_reach_host(aws_rds_host):
    assert aws_rds_host.test_can_reach_host(), "Failed to reach AWS RDS host"


# ? pytest -sv test_aws_db_connection.py::test_rds_host_connection
def test_rds_host_connection(aws_rds_host):
    assert aws_rds_host.test_can_reach_host(
    ), "Failed to reach AWS RDS host"

    version_info = aws_rds_host.connection.get_server_info()
    print(f"Connected to AWS MySQL RDS (version {version_info})")

    # * Retrieve and print detailed information about databases
    databases_info = aws_rds_host.get_database_info()
    print("List of databases:")
    for db_info in databases_info:
        print(
            f"Name: {db_info.get('Owner')}, Owner: {db_info.get('Collation')}")


def test_create_database(aws_rds_host):
    # * Check if 'your_database' exists
    your_database = aws_rds_host.database
    print(f"Initial Checking if '{your_database}' exists:")
    exists = aws_rds_host.check_database_exists(your_database)
    print(f"Checking If '{your_database}' database exists: {exists}")

    if not exists:
        print(f"'{your_database}' does not exist, attempting to create it...")
        assert aws_rds_host.create_database(
            your_database), f"Failed to create '{your_database}', test aborted."
        print("Updated List of databases:")
        databases_info = aws_rds_host.get_database_info()
        for db_info in databases_info:
            print(
                f"Name: {db_info.get('Owner')}, Owner: {db_info.get('Collation')}")
        exists = aws_rds_host.check_database_exists(your_database)
        print(f"Checking If '{your_database}' database exists: {exists}")
    else:
        print(f"The '{your_database}' database exists: {exists}")
        assert False


def test_can_reach_database(aws_database):
    assert aws_database.connect_to_database(
    ), "Connection to AWS MySQL RDS Database failed"


def test_create_table(aws_database):
    columns = {'id': 'INT', 'name': 'VARCHAR(255)', 'age': 'INT'}
    assert aws_database.create_table(
        TABLE_NAME, columns), f"Table Creation failed {TABLE_NAME}"


def test_list_tables(aws_database):
    result = aws_database.list_tables_with_columns()
    print("List of Tables with Columns:")
    print(result)
    assert result is not None, "Failed to list tables with columns"


def print_entries(entries):
    # * Check if the method returned entries
    print(f"Printing Entries")
    if entries is not None:
        for entry in entries:
            print(entry)
    else:
        print(f"Failed to list entries in table '{TABLE_NAME}'.")


def test_insert_update_delete_record(aws_database):
    table_name = TABLE_NAME
    # * Insert a record
    # * columns = {'id': 'INT', 'name': 'VARCHAR(255)', 'age': 'INT'}
    data_to_insert = {'id': 123, 'name': 'John', 'age': 40}
    record_id = aws_database.insert_record(table_name, data_to_insert)
    assert record_id != -1, "Failed to insert record"
    # * Call the method to list entries in the table
    entries = aws_database.list_entries_in_table(table_name)
    print_entries(entries)

    # * Update the inserted record
    data_to_update = {'age': '20'}
    assert aws_database.update_record(
        table_name, record_id, data_to_update), "Failed to update record"
    entries = aws_database.list_entries_in_table(table_name)
    print_entries(entries)

    # * Delete the updated record
    assert aws_database.delete_record(
        table_name, record_id), "Failed to delete record"
    entries = aws_database.list_entries_in_table(table_name)
    print_entries(entries)


def test_delete_table(aws_database):
    assert aws_database.delete_table(
        TABLE_NAME), f"Table Delete failed {TABLE_NAME}"


def test_delete_database(aws_database):
    your_database = aws_database.database
    print(f"Initial Checking if '{your_database}' exists:")
    exists = aws_database.check_database_exists(your_database)
    print(f"Checking If '{your_database}' database exists: {exists}")
    if exists:
        print(f"The '{your_database}' database exists: {exists}")
        print(f"Removing '{your_database}'...")
        assert aws_database.remove_database(
            your_database), f"Failed to remove '{your_database}'"

        print("Updated List of databases:")
        databases_info = aws_database.get_database_info()
        for db_info in databases_info:
            print(
                f"Name: {db_info.get('Owner')}, Owner: {db_info.get('Collation')}")
        exists = aws_database.check_database_exists(your_database)
        print(f"Checking If '{your_database}' database exists: {exists}")
    else:
        print(f"The '{your_database}' database DOES NOT exists: {exists}")
        assert False
