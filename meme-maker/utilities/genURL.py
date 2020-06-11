#
# Generate encoded URL to pass to function compute
# to test our meme generator
#
import urllib.parse
import json

# First, check if the local directory contains a .memeconfig file, from our last run
foundConfig = False
try:
    f = open('.memeconfig', 'r')
    config = json.loads(f.read())
    foundConfig = True
except:
    # Set blank config params
    config = {
        'functionUrl': '',
        'imgUrl': '',
        'customUrl': '',
        'topText': '',
        'bottomText': ''
    }

    print('Could not find local .memeconfig file, creating one...')

# Request user input
newConfig = {}
newConfig['functionUrl'] = input('(REQUIRED) Enter FC URL (previous: {}): '.format(config['functionUrl'])).strip()
newConfig['imgUrl'] = input('(REQUIRED) Enter image URL (previous: {}): '.format(config['imgUrl'])).strip()
newConfig['customUrl'] = input('(OPTIONAL) Enter FC custom domain name (previous: {}): '.format(config['customUrl'])).strip()
newConfig['topText'] = input('(OPTIONAL) Enter meme top text (previous: {}): '.format(config['topText'])).strip()
newConfig['bottomText'] = input('(OPTIONAL Enter meme bottom text (previous: {}): '.format(config['bottomText'])).strip()

# Update config and save to disk
for key, val in newConfig.items():
    if config[key] != val and val != '':
        config[key] = val

try:
    f = open('.memeconfig', 'w')
    f.write(json.dumps(config))
    f.close()
except:
    print('WARNING: Unable to store configuration into local .memeconfig file')

# Sanity checks (to ensure we were supplied with REQUIRED parameters)
if config['functionUrl'] == '' or 'http' not in config['functionUrl']:
    print('Sorry, function URL missing or malformed, exiting...')
    exit(-1)

if config['imgUrl'] == '' or 'http' not in config['imgUrl']:
    print('Sorry, image URL is missing or malformed, exiting...')
    exit(-1)

# Prep URL parameters
imgUrlEnc = urllib.parse.quote_plus(config['imgUrl'])
topTextEnc = urllib.parse.quote_plus(config['topText'])
bottomTextEnc = urllib.parse.quote_plus(config['bottomText'])

params = '?imgUrl=' + imgUrlEnc + '&topText=' + topTextEnc + '&bottomText=' + bottomTextEnc

# Determine function URL
if config['customUrl'] != '':
    url = 'http://' + config['customUrl'] + config['functionUrl'].split('.com')[1] + params
else:
    url = functionUrl + params

# Print out URL + parameters (can copy-paste directly into browser to
# text FC function)
print('\n' + '*' * 10)
print(url)
print('*' * 10)
