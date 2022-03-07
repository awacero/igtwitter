#!/usr/bin/env seiscomp-python

from datetime import datetime, timedelta
import sys,os

sys.path.append( os.path.join(os.environ['SEISCOMP_ROOT'],'share/gds/tools/')) 

from lib import bulletin, spooler

import tweepy
from ig_gds_utilities import ig_utilities as utilities
from db_igtwitter import TwitterDB
import logging,logging.config

logging_file = os.path.join(os.environ['SEISCOMP_ROOT'],'var/log/','gds_service_igtwitter.log')
logging.config.dictConfig({ 'version':1, 'disable_existing_loggers':True} )
logging.basicConfig(filename=logging_file, format='%(asctime)s %(message)s')
logger = logging.getLogger("igtwitter")
logger.setLevel(logging.DEBUG)


class TwitterConfig:

    def __init__(self, config):
        prefix = "twitter"
        try:
            self.accounts_file = config.get(prefix,"accounts_file")
            self.hour_limit = int(config.get(prefix,"hour_limit"))
            self.eqevent_path = config.get(prefix,"eqevent_path")
        except Exception as e:
            logger.error("##Error reading twitter config file: %s" %str(e))

        prefix = "twitter_db"
        try:
            self.db_file = config.get(prefix,"db_file")
            self.db_table_name = config.get(prefix,"db_table_name")
        except Exception as e:
            logger.error("##Error reading twitter db config file: %s" %str(e))
   
class SpoolSendTwitter(spooler.Spooler):

    def __init__(self):

        spooler.Spooler.__init__(self)
        self.twitter_config = TwitterConfig(self._config)
        logger.info("##Configuration loaded: %s" %self.twitter_config.hour_limit)
        try:
            self.twitter_accounts = utilities.read_config_file(self.twitter_config.accounts_file)
        except Exception as e:
            logger.info("Error reading twitter_accounts file: %s" %str(e))

        try:
            logger.info("Create db object. It will initialize the db if there is none")
            self.twt_db = TwitterDB(self._config)
            logger.info("## twt_db object created:%s" %self.twt_db )
        except Exception as e:
            logger.error("Error creating TwitterDB object: %s" %str(e))


    def spool(self, addresses, content):
        logger.info("##Start spool() for SpoolSendTwitter with: %s" %(addresses))

        try:
            bulletin_object = bulletin.Bulletin()
            bulletin_object.read(content)
        except Exception as e:
            raise Exception("Error starting spool(): %s" %str(e))

         

        logger.debug("Event info to tweet: %s" %(bulletin_object.plain))
        event_info = bulletin_object.plain
        event_info = event_info.split(" ")
        event_id = event_info[1].split(":")[1]
        event_status = event_info[2]
        event_datetime = datetime.strptime("%s %s" %(event_info[3],event_info[4]),"%Y-%m-%d %H:%M:%S")
        ##Create a function to create/check the image in case eqevents isn't ready.
        event_image_path = "%s/%s/%s-map.png" %(self.twitter_config.eqevent_path,event_id,event_id)
        event_dict = {'text':'%s' %bulletin_object.plain, 'path':event_image_path}

        logger.info("event info to look in db: %s %s %s" %(event_id,event_status,event_datetime))
        
        """Check if the event is within the hour_limit """
        if not self.check_antiquity(event_datetime):
            logger.info("event too old. Limit is %s hours" %self.twitter_config.hour_limit)
            return True




        for address in addresses:

            """Check against the DB if the event has been published already"""        
            select = "*"
            where = "event_id='%s'" %event_id
            rows = self.twt_db.get_post(select, where)

            for row in rows:
                if row['event_id'] == event_id and row['status'] == event_status and row['gds_target']==address[1]:
                    logger.info("Event %s already published" %event_id)
                    return True

            try:
                """Create the api to twitter"""
                logger.info("Start tweet publication")
                twitter_account = self.twitter_accounts[address[1]]                
                twitter_api = self.connect_twitter(twitter_account)         
                logger.info("Conection to twitter ok: %s" %twitter_api)   
                tweet_id = self.post_event(twitter_api,event_dict)    

                if tweet_id == False:
                    logger.error("Error posting tweet")
                    return False
                else: 
                    logger.info("Insert tweet_id into DB")
                    #event_row = {'event_id':'%s', 'tweet_id':'%s' , 'status': '%s', 'gds_target': '%s'}
                    event_row = {'event_id':event_id, 'tweet_id': tweet_id , 'status': event_status, 'gds_target': address[1]}

                    if self.twt_db.save_post(event_row) == 0:
                        logger.info("Post info inserted into DB: %s" %event_row)                
                        return True
                    else:
                        logger.info("Failed to insert tweet info into DB")
                        return False
                        

            except Exception as e:

                logger.error("Error in spool: %s" %str(e))
                raise Exception("Error in spool: %s" %str(e))

    def connect_twitter(self,token_dict):
    
        try:
            auth = tweepy.OAuthHandler(token_dict['api_key'],token_dict['api_secret'])
            auth.set_access_token(token_dict['access_token'],token_dict['secret_token'])
            #redirect=auth.get_authorization_url()
            twitter_api = tweepy.API(auth)
            return twitter_api 
        except Exception as e:
            logger.error("Error trying to connect twitter: %s" %str(e))
            raise Exception("Error trying to connect twitter: %s" %str(e))

    def post_event(self, twitter_api, event_dict):

        try:
            logger.info("Start post tweet")
            media = twitter_api.media_upload(event_dict['path'])
            tweet_id = twitter_api.update_status(status=event_dict['text'],media_ids=[media.media_id])
            logger.info("Posted event to twitter successfully")
            return tweet_id.id
        except Exception as e:
            logger.error("Error trying to post to twitter : %s" %str(e))
            return False


    def check_antiquity(self, limit_date_time):
        """ 
        Check the age of a event 
        Parameters: limit_date_time - datetime object
        """
        date_check = datetime.now() - timedelta(hours=self.twitter_config.hour_limit)
        
        if date_check < limit_date_time:
            return True
        else:
            return False

if __name__=="__main__":
    app=SpoolSendTwitter()
    app()
