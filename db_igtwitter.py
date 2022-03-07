
from asyncore import file_dispatcher
import sqlite3
import os
import logging
from ig_gds_utilities import ig_utilities as utilities 

class TwitterDB:

    def __init__(self,config):

        if type(config) == str:

            db_config = utilities.read_parameters(config)
            self.db_file = db_config['twitter_db']['db_file']
            self.db_table_name = db_config['twitter_db']['db_table_name']
        else:
            
            self.db_file = config.get('twitter_db','db_file')
            self.db_table_name = config.get('twitter_db', 'db_table_name')
        self.init_database()

    def connect_database(self):
        db_dir = os.path.dirname(self.db_file)
        if not os.path.exists(db_dir):
            logging.debug("Creating DB directory")
            os.makedirs(db_dir)

        logging.debug("connecting to BD")
        con = sqlite3.connect(self.db_file)
        con.text_factory = bytes
        logging.debug("connection to DB established")
        return con

    def close_database(self,con):
        con.commit()
        con.close()
        logging.debug("connection to DB closed")

    def init_database(self):
        logging.info("creating and starting BD")
        try:
            if os.path.isfile(self.db_file):
                return 0
            con = self.connect_database()
            cur = con.cursor()
            sql = """CREATE TABLE %s (
            event_id TEXT , tweet_id INTEGER PRIMARY KEY,status TEXT)""" % self.db_table_name
            logging.debug("Creating table %s" % self.db_table_name)
            cur.execute(sql)
            self.close_database(con)
            logging.info("Table created")
            return 0
        except sqlite3.Error as e:
            logging.info("Failed to create DB/table: %s" % str(e))
            return -1

    def save_post(self, post_dict):
        
        con = self.connect_database()
        cur = con.cursor()
        sql = """INSERT INTO %s (event_id, tweet_id, status ) 
            VALUES (:event_id,  :tweet_id, :status)""" % self.db_table_name

        try:
            cur.execute(sql, post_dict)
            logging.debug("Event '%s' added" % post_dict['event_id'])
            self.close_database(con)
            return 0

        except sqlite3.Error as e:
            logging.debug("Failed to add event %s : %s" % (post_dict['event_id'], str(e)))
            return -1


        
    def dict_factory(self,cursor, row):

        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


    def get_post(self,select="*", where=None):
        con = self.connect_database()
        con.row_factory = self.dict_factory
        con.text_factory = str
        cur = con.cursor()
        sql = "SELECT %s FROM %s " % (select, self.db_table_name)
        if where:
            sql += "WHERE %s " % where
        cur.execute(sql)
        events = cur.fetchall()
        self.close_database(con)
        return events

    def delete_post(self,event_id):
        con = self.connect_database()
        cur = con.cursor()
        sql = "DELETE FROM %s WHERE event_id='%s'" %(self.db_table_name,event_id)
        try:
            cur.execute(sql)
            con.commit()
            return True
        except sqlite3.Error as e:
            return str(e)

    def update_post(self,post_dict, column, value):
        #post_dict["table"] = configFaceTweet.tw_dbtable
        con = self.connect_database()
        cur = con.cursor()
        sql = """UPDATE %s SET %s = %s WHERE event_id= '%s'
        """ % (self.db_table_name, column, value, post_dict['event_id'])
        try:
            logging.info("SQL: %s" % sql)
            cur.execute(sql, post_dict)
            logging.info("Event %s inserting")
            self.close_database(con)
            return 0
        except sqlite3.Error as e:
            logging.error("Failed to insert value: %s. Error:  %s" % (value, str(e)))
            return -1