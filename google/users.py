#!/usr/bin/env python
# TODO: future absolute import
import os
__DIRNAME = os.path.dirname(__file__)
import sys
sys.path.append(__DIRNAME+"/../lib")


from distutils.util import strtobool
import json
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from general import Application
import pprint
pp = pprint.PrettyPrinter(indent=4)

# TODO: merge default config
# https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python-taking-union-o

## Google
# https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list
def create_directory_service(config):
  credentials = ServiceAccountCredentials.from_p12_keyfile(
      config['GWS_ACCOUNT'],
      __DIRNAME + "/../" + config['GWS_PKCS12'],
      'notasecret',
      scopes = [config['GWS_SCOPES']])
  credentials = credentials.create_delegated(config['GWS_USER'])
  return build( 'admin', 'directory_v1', credentials = credentials )
# def


## Application
class ListUsers( Application ):
  def __init__( self, file = __file__ ):
    Application.__init__( self, file )
  # def

  # 'creationTime' 'fullName' 'primaryEmail'
  # https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.users.html#list
  # Download Google Worksapce user list self.satus
  def getStatusData(self):
    self.log.debug("TODO: https://github.com/googleapis/google-api-python-client/pull/1125")
    service = create_directory_service( self.config )
    results = service.users().list( customer = 'my_customer', orderBy = 'email', projection = 'full' ).execute()
    users = results.get('users', [])

    # Set Eastern European full name
    eastern = strtobool( self.config['GWS_EASTERN_NAME_ORDER'])
    for i, user in enumerate(users):
      fullName = user['name']['fullName']
      if eastern:
        fullName = user['name']['familyName'] + " " + user['name']['givenName']
      users[i]['fullName'] = fullName
    # for

    data = { 'data': users }
    return data
  # def

  def convertStatus(self):
    self.canonicalStatus = {}
    createdAt = self.status['createdAt']
    for data in self.status['data']:
      self.canonicalStatus[data['primaryEmail']] = {**data, 'createdAt': createdAt}
    # pp.pprint(self.canonicalStatus)
    self.log.info('convertStatus: OK')
  # def


  ## Database
  # https://docs.mongodb.com/manual/core/databases-and-collections/
  # https://pymongo.readthedocs.io/en/stable/tutorial.html
  def initialize(self):
    self.db.conn_mongodb()
    # database
    db_id = self.config['GWS_DATABASE'] or 'google'
    col_id = 'gws_users'
    try:
      db = self.db.client[db_id]
      # check colletion
      collection = db[col_id]
      uid = collection.insert_one({'primaryEmail': 'test@test.test', 'fullName': 'Test Test'}).inserted_id
      obj = collection.find_one({"_id": uid})
      collection.delete_one({"_id": uid})
      # collection.drop()
      self.log.info( "TODO db.products.createIndex( { 'primaryEmaiil': 1, 'fullName': 1 } )" )
    # create collection
    # create index
    # insert update delete selftest
    except Exception as error:
      self.log.error("Database initialization failed: " + str(error))
      sys.exit(1)

    self.log.info("Database initialized: %s.%s" % (db_id,col_id))
  # def

  def upsertStatus(self):
    # https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
    self.db.conn_mongodb()
    db_id = self.config['GWS_DATABASE'] or 'google'
    col_id = 'gws_users'
    self.db.bulkUpsert(self.canonicalStatus, db_id, col_id)
# class


## MAIN
if __name__ == '__main__':
  # New Application object
  app = ListUsers()
  # Call getSatusData
  app.main()
  # store
  # https://stackoverflow.com/questions/5292370/fast-or-bulk-upsert-in-pymongo
