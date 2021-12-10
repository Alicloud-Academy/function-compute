# -*- coding: utf-8 -*-
#
# Author: Jeremy Pedersen
# Created: 2021-12-04
# Updated: 2021-12-09
# License: MIT
#
import logging
import urllib.parse, requests, json
import random, time
import mysql.connector

# 
# Database connection config
#
config = {
  'user': 'db_username',
  'password': 'db_password',
  'host': 'alibaba_cloud_db_internal_endpoint_address',
  'database': 'database_name',
  'raise_on_warnings': True
}

# NOTE: Required parameters are:
# product_id
# user_id 
# year (XXXX)
# month (X or XX)
# quantity
#
# Function will return an error if these 
# parameters aren't found or don't appear valid
def handler(environ, start_response):
    # Enable logging
    logger = logging.getLogger()

    # Get environment variables and original HTTP request URI
    context = environ['fc.context']
    request_uri = environ['fc.request_uri']

    # Try and parse URL parameters
    try:
        # Grab query parameters from the end of the URL
        params = urllib.parse.unquote_plus(request_uri)
        params = params.split('?')[-1]
        params = urllib.parse.parse_qs(params)
    except:
        retVal = 'Error: Something went wrong parsing the URL parameters. The original URL string was: {}'.format(request_uri)
        logger.info(retVal)

        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [ bytes(retVal, 'utf-8') ]
    

    # Code below checks that all of the required URL parameters are 
    # present. The code is designed to warn about ALL missing URL 
    # parameters, so checks will continue to be run even if some parameters
    # are missing or malformed. 
    allIsWell = True
    retVal = ''
    # Go through individual URL parameters (all of which are optional), pulling out
    # any we are able to find
    try:
        product_id = int(params['product_id'][0].strip('"').strip("'"))
    except:
        allIsWell = False
        retVal += 'WARNING: product_id is missing\n'

    try:
        uid = int(params['user_id'][0].strip('"').strip("'"))
    except:
        allIsWell = False
        retVal += 'WARNING: user_id is missing\n'

    try:
        year = int(params['year'][0].strip('"').strip("'"))
        if len(str(year)) != 4 or year < 0:
            allIsWell = False
            retVal += 'WARNING: year is missing or incorrectly formatted\n'  
    except:
        allIsWell = False
        retVal += 'WARNING: year is missing or incorrectly formatted\n'

    try:
        month = int(params['month'][0].strip('"').strip("'"))
        if len(str(month)) > 2 or month > 12 or month < 1:
            allIsWell = False
            retVal += 'WARNING: month is missing or incorrectly formatted\n'  
    except:
        allIsWell = False
        retVal += 'WARNING: month is missing or incorrectly formatted\n'  

    try:
        item_quantity = int(params['quantity'][0].strip('"').strip("'"))
        if item_quantity < 1:
            allIsWell = False
            retVal += 'WARNING: quantity is missing or incorrectly formatted\n' 
    except:
        allIsWell = False
        retVal += 'WARNING: quantity is missing or incorrectly formatted\n'

    # 
    # Generate new order
    # 
    if allIsWell:
        #
        # Connect to ADB
        #
        db_conn = mysql.connector.connect(**config)
        cursor = db_conn.cursor()

        # 
        # Write record to ADB
        # 
        cursor.execute(
            "INSERT INTO `orders` (year, month, product_code, quantity, user_id) VALUES ('{}', '{}', {}, {}, {});".format(year, month, product_id, item_quantity, uid)
        )
        id = cursor.lastrowid

        retVal = json.dumps(
            {
                'id': id,
                'year': year,
                'month': month,
                'product_code': product_id,
                'quantity': item_quantity,
                'user_id': uid
            }
        )

        db_conn.commit()
        cursor.close()
        db_conn.close()

    # Return results
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [ bytes(retVal, 'utf-8') ]
