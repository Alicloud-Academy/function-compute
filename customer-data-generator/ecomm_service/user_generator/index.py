# -*- coding: utf-8 -*-
#
# Author: Jeremy Pedersen
# Created: 2021-12-03
# Updated: 2021-12-09
# License: MIT
#
import logging
import urllib.parse, requests, json
import names, random, time
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

#
# Hard-coded countries and country codes (included here in the 
# body of the function to avoid having to deal with file I/O)
#
countries = [
    "Argentina",
    "Australia",
    "Belgium",
    "Brazil",
    "Canada",
    "China",
    "Denmark",
    "Egypt",
    "Ethiopia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "India",
    "Indonesia",
    "Ireland",
    "Italy",
    "Japan",
    "Kenya",
    "Kiribati",
    "Korea",
    "Luxembourg",
    "Macao",
    "Malaysia",
    "Mexico",
    "New Zealand",
    "Norway",
    "Pakistan",
    "Poland",
    "Portugal",
    "Russia",
    "Singapore",
    "South Africa",
    "Spain",
    "Sweden",
    "Switzerland",
    "Thailand",
    "Turkey",
    "Ukraine",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Vietnam"
]

country_codes = [
    "AR",
    "AU",
    "BE",
    "BR",
    "CA",
    "CN",
    "DK",
    "EG",
    "ET",
    "FI",
    "FR",
    "DE",
    "GR",
    "IN",
    "ID",
    "IE",
    "IT",
    "JP",
    "KE",
    "KI",
    "KR",
    "LU",
    "MO",
    "MY",
    "MX",
    "NZ",
    "NO",
    "PK",
    "PL",
    "PT",
    "RU",
    "SG",
    "ZA",
    "ES",
    "SE",
    "CH",
    "TH",
    "TR",
    "UA",
    "AE",
    "GB",
    "US",
    "VN"
]

# When invoked, create one or more new users, using several
# (optional) parameters as input:
# num_users = number of users to create
# sex = sex of users (M or F)
# country = country of origin (accepts full names such as 'Greece' or 'United States')
# min_age = minimum user age
# max_age = maximum user age
# Note: names are always selected at random
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
    
    # Go through individual URL parameters (all of which are optional), pulling out
    # any we are able to find. 
    try:
        num_users = int(params['num_users'][0].strip('"').strip("'"))
    except:
        num_users = 1 # Default to creating one user, if not specified or invalid

    # Sanity check
    if num_users < 1:
        num_users = 1

    try:
        sex = params['sex'][0].strip('"').strip("'").upper()
    except:
        sex = 'MISSING'

    try:
        country = params['country'][0].strip('"').strip("'").lower().title()
    except:
        country = 'MISSING'

    try:
        min_age = int(params['min_age'][0].strip('"')).strip("'")
    except:
        min_age = 18

    try:
        max_age = int(params['max_age'][0].strip('"')).strip("'")
    except:
        max_age = 100   

    #
    # Connect to ADB
    # 
    # Note: we don't wrap this in a try/except, since we want the function to 
    # explicitly fail if the connection isn't established, this will give us some
    # very obvious error messages in the HTTP response from the FC service, which
    # will help to diagnose the issue.
    db_conn = mysql.connector.connect(**config)
    cursor = db_conn.cursor()

    #
    # Generate new user(s)
    #
    retVal = ''
    for i in range(0, num_users):
        # Randomly select user's age
        age = random.randint(min_age, max_age)
        
        # Evenly distribute user sex, if none was chosen
        if sex == 'MISSING' or sex not in 'MF':
            if random.random() > 0.5:
                user_sex = 'M'
            else:
                user_sex = 'F'
        else:
            user_sex = sex

        # Choose a name appropriate to the sex selected
        if user_sex == 'M':
            name = names.get_full_name(gender='male') 
        else:
            name = names.get_full_name(gender='female')

        # Determine user's country of origin
        if country == 'MISSING' or country not in countries:
            # Choose random country of origin for user
            index = random.randint(0,len(countries)-1)
            location = countries[index]
            location_code = country_codes[index]
        else:
            location = country
            location_code = country_codes[countries.index(location)]

        # 
        # Write record to ADB
        # 
        cursor.execute(
            "INSERT INTO `users` (name, age, sex, country, country_code) VALUES ('{}', {}, '{}', '{}', '{}');".format(name, age, user_sex, location, location_code)
        )
        id = cursor.lastrowid

        # Add new user record to return value
        retVal += json.dumps(
        {
            'id': id,
            'name': name,
            'age': age,
            'sex': user_sex,
            'country': location,
            'country_code': location_code
        }
        ) + '\n'

    # Disconnect from ADB
    db_conn.commit()
    cursor.close()
    db_conn.close()

    # Return results
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [ bytes(retVal, 'utf-8') ]
