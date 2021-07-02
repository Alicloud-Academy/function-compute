import logging
import requests
import json
import urllib.parse

# Pretty-print and properly escape the JSON
# text passed to us by CloudMonitor, so that
# we can display it in Slack 
def pprint_json(leading_char, parsed_json):
    output_text = '\n'

    for key in parsed_json:
        item = parsed_json[key]

        if isinstance(item, dict): # We need to go deeper!
            output_text += key + ':'
            output_text += pprint_json(leading_char + '\t', item)
        else:
            output_text += "{}{}: {}\n".format(leading_char, key, item)

    return output_text

# Main function (called the "handler": takes JSON 
# from CloudMonitor callbacks and sends it on to 
# Slack as (nicely?) formatted text
def handler(environ, start_response):
    logger = logging.getLogger()

    context = environ['fc.context']
    request_uri = environ['fc.request_uri']

    # This code does nothing, but is left in
    # as an example of how you *could* process
    # request parameters. We don't use it as we are only
    # interested in the request body, not parameters.
    for k, v in environ.items():
      if k.startswith('HTTP_'):
        # process custom request headers
        pass

    # Determine size of request body, if it is zero we exit here: there's no need
    # to call the Slack webhook
    try:        
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))    
    except (ValueError):        
        request_body_size = 0
        err = "Request body size was zero, exiting"
        logger.info(err)
        return [err.encode()]

    # Unpack and parse the CloudMonitor request body: we will exit with an
    # error if we encounter any issues here
    try:
        request_body = environ['wsgi.input'].read(request_body_size)   
        request_body_string = urllib.parse.unquote(request_body.decode())
        request_body_json = urllib.parse.parse_qs(request_body_string)
        output = pprint_json('', request_body_json)
    except:
        err = "Something went wrong processing the request body. Check your Function Compute logs."
        logger.info(err)
        return [err.encode()]

    # Log contents of output here, to help us determine if any issues
    # were encountered
    logger.info(output)

    # URL of the Slack webhook
    end_url = 'your_slack_url_here'
    headers = {'Content-type': 'application/json'}

    # Deal with the possibility of an empty output
    if output.strip() == '' or len(output) == 0:
        output = "CloudMonitor sent an empty notification. Check your logs."

    # Send message to slack
    payload = {'text': output}
    r = requests.post(end_url, headers=headers, data=json.dumps(payload))

    # Send response (to indicate that the function has run successfully)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    # Output formatted text for debugging purposes
    return [output.encode()]
