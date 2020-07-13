# -*- coding: utf-8 -*-

#
# Author: Jeremy Pedersen
# Created: 2020-06-10
# Updated: 2020-06-11
# License: MIT
#

import logging
import oss2
import urllib.parse
import requests, io
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# Helper function to outline text in black, inspired by this
# wonderful blog article: https://blog.lipsumarium.com/caption-memes-in-python/
#
def drawOutline(drawLayer, fontType, text, coords):
    x = coords[0]
    y = coords[1]
    drawLayer.text((x-2, y-2), text,(0,0,0),font=fontType)
    drawLayer.text((x+2, y-2), text,(0,0,0),font=fontType)
    drawLayer.text((x+2, y+2), text,(0,0,0),font=fontType)
    drawLayer.text((x-2, y+2), text,(0,0,0),font=fontType)
    drawLayer.text((x, y), text, (255,255,255), font=fontType)   

def handler(environ, start_response):
    # Enable logging
    logger = logging.getLogger()

    # Get environment variables and original HTTP request URI
    context = environ['fc.context']
    request_uri = environ['fc.request_uri']

    #
    # Parameter Parsing
    #  

    # The allIsWell flag gets set to false if we encounter an error. This will prevent some
    # portions of the code from running later on (which might cause an exception), while
    # still allowing us to reach the end of the function and return a valid HTTP response
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
        imgUrl = params['imgUrl'][0].strip('"')
    except:
        imgUrl = 'MISSING'
    
    try:
        topText = params['topText'][0].strip('"')
    except:
        topText = ''

    try:
        bottomText = params['bottomText'][0].strip('"')
    except:
        bottomText = ''

    # Further processing of top and bottom text
    imgUrl = imgUrl.strip()
    topText = topText.strip().upper()
    bottomText = bottomText.strip().upper()

    # The imgUrl parameter is required, so we need to gracefully give up if
    # it is missing or malformed
    if allIsWell:
        if imgUrl == 'MISSING' or not imgUrl.startswith('http'):
            retVal = 'Error: imgUrl parameter is missing or malformed. The imgUrl parameter password was: {}'.format(imgUrl)
            logger.info(retVal)
            allIsWell = False

        # We only support PNG and JPG formats for now, we need to return with
        # an error if we were passed a link that is not an image file
        # in one of these two formats.
        try:
            imgType = imgUrl.split('.')[-1].lower()
        except:
            retVal = 'Error: Unable to determine image file extension...are you sure this is an image file?'
            logger.info(retVal)
            allIsWell = False

    #
    # Image processing
    #

    # First, fetch the image
    if allIsWell:
        r = requests.get(imgUrl)
    
        if r.status_code != 200:
            retVal = 'Error: failed to fetch image. The status code was {}, and the image URL was: {}'.format(r.status_code, imgUrl)
            logger.info(retVal)
            allIsWell = False

    # Then, meme-ify the image
    # Prepare the image for captioning using Python's PIL
    if allIsWell:
        img = Image.open(io.BytesIO(r.content))
        drawLayer = ImageDraw.Draw(img)

        # Loop until we find a font size that will allow both the top
        # and bottom text to fit comfortably on a single line. This 
        # way we can avoid any issues with splitting lines or working out
        # centering and padding for multiple lines
        fontSize = 200 # Start at an enormous size, for high resolution images
        while True:
            fontType = ImageFont.truetype("oswald_bold.ttf", fontSize)
            # Determine the width and height of the top and bottom text
            widthTop, heightTop = drawLayer.textsize(topText, fontType)
            widthBottom, heightBottom = drawLayer.textsize(bottomText, fontType)

            # Check to see if either the top or bottom text is too big to fit
            topExceedsMaxWidth = widthTop >= img.width * 0.8
            bottomExceedsMaxWidth = widthBottom >= img.width * 0.8

            # Quit when we reach a reasonable size
            if not topExceedsMaxWidth and not bottomExceedsMaxWidth:
                break

            fontSize -= 1

            # Check if the fontsize shrinks to nothing
            if fontSize < 1:
                print("Something has gone terribly wrong...")
                exit(-1)

        # Draw font on image
        drawOutline(drawLayer, fontType, topText, (img.width/2 - widthTop/2, 0))
        drawOutline(drawLayer, fontType, bottomText, (img.width/2 - widthBottom/2, img.height - (heightBottom + heightBottom/4)))

        # Create another BytesIO stream for outputting the image content
        output = io.BytesIO()
        img.save(output, format='JPEG')

    # Last, return the final result
    if allIsWell:
        status = '200 OK'
        response_headers = [('Content-type', 'image/jpeg'), ('Content-Disposition', 'inline; filename="meme.jpeg"')]
        start_response(status, response_headers)
        return [ output.getvalue() ]
    else:
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [ bytes(retVal, 'utf-8') ]
