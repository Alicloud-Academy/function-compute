# -*- coding: utf-8 -*-
#
# Author: Jeremy Pedersen
# Created: 2020-10-20
# Updated: 2020-10-20
# License: MIT
#
import logging
import urllib.parse

# Pull in Alibaba Cloud Python SDK so we can make the
# CreateSnapshot() API call
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkecs.request.v20140526.CreateSnapshotRequest import CreateSnapshotRequest

###########
# GLOBALS #
###########
access_key = "ak_key" # Ex: LTAI5tSArY9Zgi41tbGGovQe
secret = "ak_secret" # Ex: 4KJY6vQ3RGc4rn8KDOGSWT4xm9iz9N
region = "region" # Ex: ap-southeast-1

# Main body of our FC function
def handler(environ, start_response):
    # Enable logging
    logger = logging.getLogger()

    # Get environment variables and original HTTP request URI
    context = environ['fc.context']
    request_uri = environ['fc.request_uri']

    #
    # Parameter Parsing
    # 

    # The allIsWell flag gets set to false if we encounter an error. 
    # This will prevent some portions of the code from running later on 
    # (which might cause an exception), while still allowing us to reach 
    # the end of the function and return a valid HTTP response
    # to the user.
    allIsWell = True 

    # Parse query parameters
    try:
        # Grab query parameters from the end of the URL
        params = urllib.parse.unquote_plus(request_uri)
        params = params.split('?')[-1]
        params = urllib.parse.parse_qs(params)
    except:
        retVal = 'Error: Something went wrong parsing the URI parameters. The original URI string was: {}'.format(request_uri)
        logger.info(retVal)
        allIsWell = False
    
    # Pull out parameter values (strip quotes, in case
    # quotes were included in the original parameters)
    try:
        diskID = params['diskID'][0].strip('"')
    except:
        diskID = ''

    # Further processing to strip whitespace
    diskID = diskID.strip()

    # A diskID is required to make the CreateSnapshot API call, so we will check
    # here that a valid ID was provided. If not, we'll have to make a graceful exit.
    if allIsWell:
        if diskID == '':
            retVal = 'Error: diskID (a required parameter) was missing. Try again. The full URI passed to the function was: {}'.format(request_uri)
            logger.info(retVal)
            allIsWell = False

    #
    # CreateSnapshot call
    #
    if allIsWell:

        client = AcsClient(access_key, secret, region)

        request = CreateSnapshotRequest()
        request.set_accept_format('json')
        request.set_DiskId(diskID)
        response = client.do_action_with_exception(request)
        retVal = str(response, encoding='utf-8')


    #
    # Return 
    #
    if allIsWell:
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [ bytes(retVal, 'utf-8') ]
    else:
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [ bytes(retVal, 'utf-8') ]
