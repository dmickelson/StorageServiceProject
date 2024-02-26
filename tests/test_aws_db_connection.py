import pytest
import pymysql
import socket

# ? pytest -v test_aws_db_connection.py


@pytest.fixture
def rds_host():
    return 'database-1.clkmgeoe0nsn.us-east-1.rds.amazonaws.com'


def test_can_reach_host(rds_host):
    port = 3306
    try:
        with socket.create_connection((rds_host, port), timeout=5):
            pass
        print(f"Can reach AWS RDS host: {rds_host}")
    except Exception as e:
        pytest.fail(f"Failed to reach AWS RDS host: {rds_host}, Error: {e}")


@pytest.fixture
def db_connection():
    # * Replace these with your actual AWS RDS credentials
    host = 'database-1.clkmgeoe0nsn.us-east-1.rds.amazonaws.com'
    user = 'admin'
    password = 'r18&GL#i'

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password
    )

    yield connection

    # * Close the connection after the test
    if connection.open:
        connection.close()
        print("Connection closed")


def test_database_connection(db_connection):
    assert db_connection.open, "Connection to AWS MySQL RDS failed"

    version_info = db_connection.get_server_info()
    print(f"Connected to AWS MySQL RDS (version {version_info})")

    # * Retrieve and print detailed information about databases
    databases_info = get_database_info(db_connection)
    print("List of databases:")
    for db_info in databases_info:
        print(
            f"Name: {db_info['Database']}, Owner: {db_info['Owner']}, Collation: {db_info['Collation']}")

    # * Check if 'database-1' exists
    print("Checking if 'database-1' exists:")
    exists = check_database_exists(db_connection, 'database-1')
    print(f"Checking If 'database-1' database exists: {exists}")

    if not exists:
        print("'database-1' does not exist, attempting to create it...")
        create_database(db_connection, 'database-1')
        exists = check_database_exists(db_connection, 'database-1')
        assert exists, "Failed to create 'database-1', test aborted."

    print(f"The 'database-1' database exists: {exists}")

    # * Additional test logic can be added here...

    # * Remove 'database-1' if it was created during the test
    if exists:
        print("Removing 'database-1'...")
        remove_database(db_connection, 'database-1')


def get_database_info(connection):
    """Retrieve detailed information about databases."""
    databases_info = []
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            result = cursor.fetchall()
            for db_name in [item[0] for item in result]:
                db_info = get_database_properties(connection, db_name)
                databases_info.append(db_info)
    except Exception as e:
        print(f"Error fetching database information: {e}")
    return databases_info


def get_database_properties(connection, database_name):
    """Retrieve properties of a database."""
    db_info = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW CREATE DATABASE {database_name}")
            result = cursor.fetchone()
            if result:
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
                db_info['Database'] = database_name
                db_info['Owner'] = owner
                db_info['Collation'] = collation
    except Exception as e:
        print(f"Error fetching database properties: {e}")
    return db_info


def check_database_exists(connection, database_name):
    """Check if a database exists."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Error checking if database exists: {e}")
        return False


def create_database(connection, database_name):
    """Create a database."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully.")
    except Exception as e:
        print(f"Error creating database '{database_name}': {e}")


def remove_database(connection, database_name):
    """Remove a database."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE {database_name}")
        print(f"Database '{database_name}' removed successfully.")
    except Exception as e:
        print(f"Error removing database '{database_name}': {e}")


if __name__ == '__main__':
    pytest.main(['-s', 'test_aws_db_connection.py'])
