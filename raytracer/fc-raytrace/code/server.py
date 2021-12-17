import time
from flask import Flask
from flask import request
from flask import send_file
import json
import sys
import traceback
import logging
import subprocess # Added to allow us to call smallpt

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

REQUEST_ID_HEADER = 'x-fc-request-id'

#
# Simple Flask code to handle incoming GET requests
#
@app.route('/', methods=['GET'])
def raytrace():
    # See FC docs for all the HTTP headers: https://www.alibabacloud.com/help/doc-detail/132044.htm#common-headers
    request_id = request.headers.get("x-fc-request-id", "")
    print("FC Invoke Start RequestId: " + request_id)

    # Process URL params (SPP = samples per pixel)
    # which decides the quality of our output image
    print("Attemping to read URL params")
    try:
        spp = int(request.args.get('spp').strip())
    except:
        print("Unable to read URL params, exiting")
        return 'Sorry, could not find spp (samples per pixel) URL parameter, or the parameter was not an integer'

    # Produce image
    print("Attempting to run raytracer as: ./smallpt {}".format(spp))
    try:
        subprocess.run(['./smallpt', '{}'.format(spp)])
    except:
        print("Unable to run raytracer, exiting")
        return 'Sorry, failed to run smallpt raytracer'

    # Return image
    print("Attempting to return image file")
    filename = 'image.ppm' # File produced by smallpt
    return send_file(filename, mimetype='image/ppm') 

# Code left as-is, in the original example 
# here: https://github.com/devsapp/start-fc
class CustomProxyFix(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        host = environ.get('HTTP_HOST', '')
        region = environ.get('HTTP_X_FC_REGION', '')
        uid = environ.get('HTTP_X_FC_ACCOUNT_ID', '')
        serviceName = environ.get('HTTP_X_FC_SERVICE_NAME', '')
        functionName = environ.get('HTTP_X_FC_FUNCTION_NAME', '')
        if host == "{0}.{1}.fc.aliyuncs.com".format(uid, region) or \
                "localhost" in host or \
                "127.0.0.1" in host:
            environ['SCRIPT_NAME'] = "/2016-08-15/proxy/{0}/{1}".format(
                serviceName, functionName)
            environ['PATH_INFO'] = environ['PATH_INFO'].replace(
                environ['SCRIPT_NAME'], "")
            print(environ)
        return self.app(environ, start_response)

app.wsgi_app = CustomProxyFix(app.wsgi_app)
