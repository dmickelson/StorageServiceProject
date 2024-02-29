import pytest
from storageservice import awsmysqllib
from typing import Dict, Union

# Set your actual AWS RDS credentials
AWS_RDS_HOST = 'your_rds_host'
AWS_RDS_USER = 'your_rds_user'
AWS_RDS_PASSWORD = 'your_rds_password'
AWS_RDS_DATABASE = 'your_database'
AWS_RDS_PORT = 3306  # Change to your actual port


# ? Set your actual AWS RDS credentials
AWS_RDS_CONFIG_FILE = 'awsmysql.cfg'  # Change to your actual file path

# ? pytest -v test_aws_db_connection.py


@pytest.fixture
def aws_database():
    aws_db = awsmysqllib.AWSMySQLLib.init_from_file(AWS_RDS_CONFIG_FILE)
    aws_db.connect_to_database()
    yield aws_db
    aws_db.close_connection()


def test_can_reach_host(aws_database):
    assert aws_database.test_can_reach_host(), "Failed to reach AWS RDS host"


def test_database_connection(aws_database):
    assert aws_database.connect_to_database(), "Connection to AWS MySQL RDS failed"

    version_info = aws_database.connection.get_server_info()
    print(f"Connected to AWS MySQL RDS (version {version_info})")

    # Retrieve and print detailed information about databases
    databases_info = aws_database.get_database_info()
    print("List of databases:")
    for db_info in databases_info:
        print(
            f"Name: {db_info.get('Owner', 'N/A')}, Owner: {db_info.get('Collation', 'N/A')}")

    # Check if 'your_database' exists
    print("Checking if 'your_database' exists:")
    exists = aws_database.check_database_exists('your_database')
    print(f"Checking If 'your_database' database exists: {exists}")

    if not exists:
        print("'your_database' does not exist, attempting to create it...")
        assert aws_database.create_database(
            'your_database'), "Failed to create 'your_database', test aborted."
        print("Updated List of databases:")
        for db_info in databases_info:
            print(
                f"Name: {db_info.get('Owner', 'N/A')}, Owner: {db_info.get('Collation', 'N/A')}")

    print(f"The 'your_database' database exists: {exists}")

    # Additional test logic can be added here...

    # Remove 'your_database' if it was created during the test
    if exists:
        print("Removing 'your_database'...")
        assert aws_database.remove_database(
            'your_database'), "Failed to remove 'your_database'"


def test_insert_update_delete_record(aws_database):
    table_name = 'your_table'  # Replace with your actual table name

    # Insert a record
    data_to_insert = {'column1': 'value1', 'column2': 'value2'}
    record_id = aws_database.insert_record(table_name, data_to_insert)
    assert record_id != -1, "Failed to insert record"

    # Update the inserted record
    data_to_update = {'column1': 'new_value1', 'column2': 'new_value2'}
    assert aws_database.update_record(
        table_name, record_id, data_to_update), "Failed to update record"

    # Delete the updated record
    assert aws_database.delete_record(
        table_name, record_id), "Failed to delete record"
