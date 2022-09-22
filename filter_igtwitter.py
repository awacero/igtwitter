#!/usr/bin/env seiscomp-python

import sys
import os
import seiscomp3.Core
import seiscomp3.DataModel
import logging
import logging.config
import pytz
from lib import bulletin
from lib.filter import Filter
from datetime import datetime
from ig_gds_utilities import ig_utilities as utilities


<<<<<<< HEAD
sys.path.append(os.path.join(os.environ['SEISCOMP_ROOT'], 'share/gds/tools/'))


logging_file = os.path.join(os.environ['SEISCOMP_ROOT'], 'var/log/', 'gds_service_igtwitter.log')
=======


logging_file = os.path.join(os.environ['SEISCOMP_ROOT'],'var/log/','gds_service_igtwitter.log')
>>>>>>> dd4f55c40efc94b49991168c3cf4c6ce36991797
logging.basicConfig(filename=logging_file, format='%(asctime)s %(message)s')
logger = logging.getLogger("igtwitter")
logger.setLevel(logging.DEBUG)


class TwitterFilterConfig():

    def __init__(self):
        """
        Load config parameters

        :param self TwitterFilterConfig: Configuration object
        :returns: configuration loaderr
        """

        self.config = utilities.read_parameters(utilities.config_path)


class TwitterFilter(Filter):

    def filter(self, event_parameter):
        """
        Take an event_parameter object and return an event_bulletin object

        :param event_parameter: SwigPyObjects not serializable
        :returns: event_bulletin
        """

        twt_cfg = utilities.read_parameters(utilities.config_path)
<<<<<<< HEAD
=======
        '''
        import sys
        print("Event parameter passed by gds")
        print(type(event_parameter))
        print(event_parameter)
        event_parameter_file = open('/tmp/event_parameter_file','wb')
        import pickle
        pickle.dump(event_parameter,event_parameter_file)
        '''

>>>>>>> dd4f55c40efc94b49991168c3cf4c6ce36991797

        logger.info("start igtwitterFilter")
        try:
            event = self.parseEventParameters(event_parameter)
            event_bulletin = bulletin.Bulletin()
            event_bulletin.plain = "#SISMO ID:{id} {mode} {time_local} TL Magnitud: {magVal}" \
                                   " Profundidad: {depth} km, {nearest_city}, Latitud: {lat} Longitud:{lon}" \
                                   " {event_country}. Sintió este sismo? Repórtelo en {survey_url} ".format(**event)

            logger.info("Create map if it does not exist yet")
            event_image_path = "{0}/{id}/{id}-map.png".format(twt_cfg['ig_info']['eqevent_page_path'], **event)
            event_path = "{0}/{id}/".format(twt_cfg['ig_info']['eqevent_page_path'], **event)
            event_info = {'event_id': event['id']}

            if not os.path.isfile(event_image_path):
                logger.info("create map ")
                if not os.path.exists(event_path):
                    os.makedirs(event_path)
                map_result = utilities.generate_google_map(event['lat'], event['lon'], event_info)

                if map_result is False:
                    map_result = utilities.generate_gis_map(event['lat'], event['lon'], event_info)

            return event_bulletin

        except Exception as e:
            logger.error("Error in igtwitterFilter was: %s" % str(e))
            return None

    def parseEventParameters(self, event_parameter):
        """
        Take an event_parameter object and return an event dictionary

        :param event_parameter: SwigPyObjects not serializable
        :returns: event
        """

        event = {}
        event["id"] = ""
        event["region"] = ""
        event["magVal"] = ""
        event["time"] = ""
        event["lat"] = ""
        event["lon"] = ""
        event["depth"] = ""
        event["mode"] = ""
        event["type"] = ""
        event["nearest_city"] = ""
        event["time_local"] = ""
        event['survey_url'] = ""

        if event_parameter.eventCount() > 1:
            logger.info("More than one event. Return empty dictionary")
            return event

        event_object = event_parameter.event(0)
        event["id"] = event_object.publicID()

        for j in range(0, event_object.eventDescriptionCount()):
            ed = event_object.eventDescription(j)
            if ed.type() == seiscomp3.DataModel.REGION_NAME:
                event["region"] = ed.text()
                break

        magnitude = seiscomp3.DataModel.Magnitude.Find(event_object.preferredMagnitudeID())
        if magnitude:
            event['magVal'] = "%0.1f" % magnitude.magnitude().value()

        origin = seiscomp3.DataModel.Origin.Find(event_object.preferredOriginID())
        if origin:
            event["time"] = origin.time().value().toString("%Y-%m-%d %T")
            event["time_local"] = self.get_local_datetime(event["time"]).strftime('%Y-%m-%d %H:%M:%S')
            event["lat"] = "%.2f" % origin.latitude().value()
            event["lon"] = "%.2f" % origin.longitude().value()

            try:
                event["depth"] = "%.0f" % origin.depth().value()
            except seiscomp3.Core.ValueException:
                pass
            try:
                event["mode"] = "%s" % seiscomp3.DataModel.EEvaluationModeNames.name(event_parameter.origin(0).evaluationMode())
            except:
                event["mode"] = "automatic"
            try:
                typeDescription = event_object.type()
                event["type"] = "%s" % seiscomp3.DataModel.EEventTypeNames.name(typeDescription)
            except:
                event["type"] = "NOT SET"

            event["nearest_city"] = utilities.get_closest_city(origin.latitude().value(), origin.longitude().value())
            event["survey_url"] = str(utilities.get_survey_url(self.get_local_datetime(event['time']), event['id']))
            event["event_country"] = utilities.get_message_by_country_twitter(origin.latitude().value(), origin.longitude().value())
            event["mode"] = self.status(event["mode"])
        return event

    def status(self, stat):
        """
        Take an stat string and return the same stat string with reassigned value

        :param stat: String
        :returns: stat
        """
        if stat == 'automatic':
            stat = 'Preliminar'
        elif stat == 'manual':
            stat = 'Revisado'
        else:
            stat = '-'
        return stat

    def get_local_datetime(self, datetime_utc_str):
        """
        Take a datetime_utc_str string and return a datetime_EC string

        :param datetime_utc_str: String
        :returns: datetime_EC
        """
        # REPLACE BY A CONFIG PARAMETER

        local_zone = pytz.timezone('America/Guayaquil')
        datetime_UTC = datetime.strptime(datetime_utc_str, '%Y-%m-%d %H:%M:%S')
        datetime_EC = datetime_UTC.replace(tzinfo=pytz.utc).astimezone(local_zone)
        return datetime_EC


if __name__ == "__main__":
    app = TwitterFilter()
    sys.exit(app())
