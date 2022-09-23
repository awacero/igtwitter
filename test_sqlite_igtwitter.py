
from  db_igtwitter import TwitterDB
import os
home = os.environ['HOME']
config_file = '/%s/Documents/ProjectsPasantias/igtwitter/send_igtwitter.cfg' %home

def test_object():

    sqlite_object = TwitterDB(config_file)
    print(sqlite_object.db_file)



def test_connect_database():

    db_object = TwitterDB(config_file)
    db_connection = db_object.connect_database()
    print(db_connection)


def test_close_database():

    db_object = TwitterDB(config_file)
    db_connection = db_object.connect_database()
    db_object.close_database(db_connection)

def test_save_post():

    event_dict = {'event_id':'igepn2022xxxx', 'tweet_id': 12345_678, 'status':'manual','gds_target':'test'}

    db_object = TwitterDB(config_file)
    db_connection = db_object.connect_database()

    db_object.save_post(event_dict)


def test_get_post():

    event_dict = {'event_id':'igepn2022xxxx', 'tweet_id': 12345_678, 'status':'manual','gds_target':'test'}
    where_sql = "event_id = '%s'" %(event_dict['event_id'])
    db_object = TwitterDB(config_file)
    db_connection = db_object.connect_database()
    post = db_object.get_post(where_sql)
    print(post)



test_object()
test_connect_database()

test_close_database()

test_save_post()

test_get_post()
