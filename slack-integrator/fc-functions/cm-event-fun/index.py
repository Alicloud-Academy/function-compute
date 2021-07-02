import logging
import requests
import json

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

def handler(event, context):
  # Get logging info
  logger = logging.getLogger()

  # Log entire raw event in case we need to do troubleshooting later
  logger.info(event)

  # Load JSON-formatted event data
  evt = json.loads(event)

  # Convert JSON-formatted event data into pretty-printed format for
  # display in slack
  msg = pprint_json('', evt)

  # URL of the Slack webhook
  end_url = 'your_slack_url_here'
  headers = {'Content-type': 'application/json'}

  # Send message to slack
  payload = {'text': msg}
  r = requests.post(end_url, headers=headers, data=json.dumps(payload))
  
  return 'ok'