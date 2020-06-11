#
# Python Meme Generator
# 
# Given an image URL, top text, and bottom text, this 
# script will generate a meme using Python's PIL
#
# Author: Jeremy Pedersen
# Created: 2020-06-10
# Updated: 2020-06-10
#
# License: MIT
import requests, sys, io
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#
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

if len(sys.argv) < 4:
    print('Whoops! You must include an image URL, top text, and bottom text, like this:\n')
    print('python3 {} https://grumpycat.com/grumpy.jpg "I am" "So Grumpy"'.format(sys.argv[0]))
    exit(-1)

# Parse inputs
imgUrl = sys.argv[1].strip()

if not imgUrl.startswith('http'):
    print('Sorry your image URL is invalid: {}'.format(imgUrl))

topText = sys.argv[2].strip().upper()
bottomText = sys.argv[3].strip().upper()

# DEBUG
# print('DEBUG:\n imgUrl: {}\n topText: {}\n bottomText: {}'.format(imgUrl, topText, bottomText))

# Fetch the image
r = requests.get(imgUrl)

# Prepare the image for captioning using Python's PIL
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

# Save original image (for reference)
imgName = imgUrl.split('/')[-1].strip()
f = open(imgName, 'wb')
f.write(r.content)
f.close()

# Save meme-ified output
img.save('NEW_' + imgName)
