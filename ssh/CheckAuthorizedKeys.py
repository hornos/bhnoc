#!/usr/bin/env python
# TODO: future absolute import
import os
__DIRNAME = os.path.dirname(__file__)
import sys
sys.path.append(__DIRNAME+"/../lib")

from general import Application

## Application
class CheckAuthorizedKeys( Application ):
  def __init__( self, __file = __file__ ):
    Application.__init__( self, __file )
  # def

  def defaultArgumentParser(self):
    self.arg_parser.add_argument('--debug',default=False, action='store_true', help='Run in debug mode (verbose logging)')

  # /etc/ssh/sshd_config
  # # Apply the AuthorizedKeysCommands to the account1 user only
  # Match User account1
  #   AuthorizedKeysCommand CheckAuthorizedKeys.sh -u %u -f %f -k %k -t %t
  #   AuthorizedKeysCommandUser nobody
  # Match all
  # # End match, settings apply to all users again

  # AuthorizedKeysCommand
  #   %u - The username.
  #   %f - The fingerprint of the key or certificate.
  #   %k - The base64-encoded key or certificate for authentication.
  #   %t - The key or certificate type.
  #   
  def customArgumentParser(self):
    self.arg_parser.add_argument('-u', required=True, help='The username')
    self.arg_parser.add_argument('-f', required=True, help='The fingerprint of the key or certificate.')
    self.arg_parser.add_argument('-k', required=True, help='The base64-encoded key or certificate for authentication.')
    self.arg_parser.add_argument('-t', required=True, help='The key or certificate type.')
  # def

  def main(self):
    print("OK")

## MAIN
if __name__ == '__main__':
  app = CheckAuthorizedKeys()
  app.main()