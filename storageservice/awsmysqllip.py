import configparser
import pymysql

host = 'database-1.clkmgeoe0nsn.us-east-1.rds.amazonaws.com'
user = 'admin'
password = 'r18&GL#i'
database = 'database-1'
port = 3306

# zoho_auth.init_from_file('zohoauth.cfg')

try:
    connection = pymysql.connect(
        host=host, user=user, password=password, database=database, port=port)
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()
        print("Database version: {} ".format(version[0]))
    connection.close()
except Exception as e:
    print(f"Error: {e}")


# def init_from_file(self, file_name: str) -> None:
#        self.logger.info("Loading configuration from file: "+file_name)
#        # * read token in from a Config formated file. Requires the ZOHO_AUTH section
#        config = configparser.ConfigParser()
#        config.read(file_name)
#        try:
#             details = config['ZOHO_AUTH']
    #     self._client_id = details['client_id']
    #     self._client_secret = details['client_secret']
    #     self._redirect_url = details['redirect_url']
    #     self._refresh_token = details['refresh_token']
    #     self._access_token = details['access_token']
    #     self._expires_in = datetime.datetime.strptime(
    #         details['expires_in'], '%Y-%m-%d %H:%M:%S')
    # except configparser.NoOptionError as err:
    #     self.logger.exception("configparser.NoOptionError:")
    #     self.logger.exception(err)
    # return cls(details['client_id'], details['client_secret'], details['redirect_url'], details['refresh_token'], details['access_token'])
