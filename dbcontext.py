import pandas as pd
import sqlalchemy as alchemy
import cx_Oracle as oracle
from dotenv import dotenv_values

config = dotenv_values('.env')

oracle.init_oracle_client('./instantclient_21_6')

class dbcontext():
    def __init__(self, user=None, password=None):


        # if user == None and password == None:
        #     try:
        #         user = config['user']
        #         password = config['password']
        #     except KeyError as e:
        #         print(f"W pliku środowiskowym nie znaleziono kluczy przynależnych do logowania.")

        # self.engine = alchemy.create_engine(f"oracle+cx_oracle://{user}:{password}@{config['IPA']}:{config['PORT']}/?service_name={config['DBN']}&encoding=UTF-8&nencoding=UTF-8")

    def is_connection(self):
        try:
            with self.engine.connect() as connection:
                with connection.begin():
                    r1 = connection.execute("select * from tab")
        except alchemy.exc.SQLAlchemyError as e:
            self.exc = str(e)
            return False
        return True

    def query(self, sql_string):
        return pd.read_sql(sql_string, con=self.engine)

x = dbcontext()