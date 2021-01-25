import os
import argparse
# import configparser
# https://pypi.org/project/python-dotenv/
from dotenv import load_dotenv, find_dotenv, dotenv_values
import logging.handlers
from datetime import datetime
from distutils.util import strtobool

import pprint
pp = pprint.PrettyPrinter(indent=4)

import asyncio
from periodic import Periodic

# import json
# import time
# from datetime import datetime
# from dateutil import tz
# import json
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# import logging
# import moment
# import uuid
# import logging.handlers
# from datetime import datetime
# from db import conn_mongodb

from database import Database

# GLOBALS
__DIRNAME = os.path.dirname(__file__)
__BASENAME = os.path.basename(__file__)


def utc2local(date):
  from_zone = tz.tzutc()
  to_zone = tz.tzlocal()
  # utc = datetime.utcnow()
  utc = date # datetime.strptime("%s" % date, '%Y-%m-%d %H:%M:%S')
  # Tell the datetime object that it's in UTC time zone since 
  # datetime objects are 'naive' by default
  utc = utc.replace(tzinfo=from_zone)
  # Convert time zone
  local = utc.astimezone(to_zone)
  return local
# def

class Application:
  def __init__(self, __file = __file__ ):
    self.__file__ = __file
    # TODO: https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format
    logging.basicConfig(
      format="[%s] " % (os.path.basename(self.__file__))  + '%(asctime)s %(levelname)-8s %(message)s',
      level=logging.INFO,
      datefmt='%Y-%m-%d %H:%M:%S')
    self.log = logging.getLogger(__name__)

    ## CLI Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug',default=False, action='store_true', help='Run in debug mode (verbose logging)')
    parser.add_argument('--production',default=False, action='store_true', help='Run in production mode')
    parser.add_argument('--list',default=False, action='store_true', help='List canonical status in a table')
    parser.add_argument('--initialize',default=False, action='store_true', help='Initialize database or anything else (run only once first time)')
    parser.add_argument('--loop',type=int, help='Run in every LOOP sec')
    self.customArgumentParser(parser)
    self.arguments = parser.parse_args()

    env = os.environ.get('DOTENV') or os.path.dirname(self.__file__) + "/.env"
    self.log.info("Dotenv: " + env)
    self.config = dotenv_values( env )

    if self.arguments.debug:
      self.log.setLevel(logging.DEBUG)
    self.log.debug(os.environ)
    self.log.debug(self.config)

    # Config
    # self.config = configparser.ConfigParser()
    # self.config.read( self.args.config )

    self.log.debug( pp.pformat( vars(self) ) )
    self.db = Database(self.arguments, self.config)
  #def

  def customArgumentParser(self,parser):
    pass

  def initialize(self):
    pass

  def selfcheck(self):
    pass

  def main(self):
    if self.arguments.initialize:
      return self.initialize()
    if self.arguments.loop:
      loop = asyncio.get_event_loop()
      loop.create_task(self.startPeriodic())
      return loop.run_forever()
    # default
    # calls self.getSatusData
    self.getStatus()
    # converts status to assoc array for bulk upsert
    self.convertStatus()

    if self.arguments.list:
      self.showStatus()

    if self.arguments.production:
      self.upsertStatus()
  # def

  ## STATUS
  def showStatus(self):
    pass

  def getSatusData(self):
    pass

  def getStatus(self):
    self.log.debug('request getStatus')
    try:
      self.status = self.getStatusData()
      self.status['error'] = None
    except Exception as error:
      self.status = { 'error': error, 'data': {} }
      self.log.error(error)
      # self.status['_id'] = uuid.uuid1()
    else:
      self.log.info("getStatus: success (%d)" % len(self.status['data']))
    # moment.now().format("YYYY-MM-DDTHH:mm:ssZ") # datetime.utcnow() #  int(round(time.time() * 1000)) # datetime.utcnow()
    self.status['createdAt'] = datetime.utcnow()
    self.log.debug('getStatus: ' + pp.pformat( self.status ) )
    # pp.pprint(self.status)
  #def

  def upsertStatus(self, db_id, col_id):
    # https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
    self.db.bulkUpsert(self.canonicalStatus, db_id, col_id)

  def convertStatus(self):
    self.canonicalStatus = self.status

  ## PERIODIC
  async def periodically(self):
    self.log.info("Start periodic processing...")
    self.processStatus()
    self.log.info("Start waiting: %s s" % (self.arguments.loop))

  async def startPeriodic(self):
    p = Periodic(self.arguments.loop, self.periodically)
    await p.start(0)

#  def findOne(self,key=None, value=None):
#    # https://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
#    return next((item for item in self.status['data'] if item[key] == value), None)
#
#  def insertData(self):
#    client = conn_mongodb( self.config['mongo'] )
#    db = client['raynet']
#    # pp.pprint(self.status)
#    # print(self.config[self._basename]['collection'])
#    collection = db[self.config[self._basename]['collection']]
#    insert_id = collection.insert_one(self.status).inserted_id
#    client.close()
#    logging.info("%s: New log inserted: %s" % (self._basename, insert_id))

#def