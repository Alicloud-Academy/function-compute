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

# When invoked, creates one new product
# and inserts it into the database: accepts
# NO parameters, each product has a random name
# and price
def handler(environ, start_response):
    # Enable logging
    logger = logging.getLogger()

    # Get environment variables and original HTTP request URI
    context = environ['fc.context']
    request_uri = environ['fc.request_uri']

    #
    # Generate new product
    #

    # Create a fake, IKEA-style product name by mixing random vowels and consonants
    # according to the pattern "CVCCVC"
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    lc = len(consonants) - 1
    lv = len(vowels) - 1

    # Set name
    product = ''.join([
        consonants[random.randint(0,lc)],
        vowels[random.randint(0,lv)],
        consonants[random.randint(0,lc)],
        consonants[random.randint(0,lc)],
        vowels[random.randint(0,lv)],
        consonants[random.randint(0,lc)]
    ]).title()

    # Set price (1 - 1000 USD)
    price = round(random.random() * 999 + 1, 2)

    # Connect to ADB
    db_conn = mysql.connector.connect(**config)
    cursor = db_conn.cursor()

    cursor.execute(
        "INSERT INTO `products` (product_name, price) VALUES ('{}', {});".format(product, price)
    )
    id = cursor.lastrowid

    retVal = json.dumps(
        {
            'id': id,
            'name': product,
            'price': price
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
