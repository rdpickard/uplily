import os
from urllib.parse import urlparse
import sys

import flask
from werkzeug.utils import secure_filename


application = flask.Flask(__name__)

uploads_dir = "file:///tmp/"

# P validate the uploads location
save_url = urlparse(uploads_dir)
if save_url.scheme not in ('file', 's3'):
    application.logger.error("Uploads location scheme [{}] is not supported".format(save_url.scheme))
    sys.exit(-1)
if save_url.scheme == 'file':
    if not os.path.exists(save_url.path):
        try:
            os.makedirs(save_url.path)
        except Exception as mkdirerr:
            application.logger.critical("Could not create uploads directory [{}] on local "
                                        "file system. Err [{}]".format(save_url.path, mkdirerr))
            raise mkdirerr


@application.route('/', methods=['POST'])
@application.route('/uplily', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in flask.request.files:
        return "No file detected"
    file = flask.request.files['file']

    if file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)

    if save_url.scheme == 'file':
        application.logger.debug(os.path.join(save_url.path, filename))
        file.save(os.path.join(save_url.path, filename))
    else:
        return "Can't save file. Uploads scheme [{}] unsupported".format(save_url.scheme)
    return "OK"


@application.route('/')
def index():
    """
    Renders the 'index' page
    :return:
    """
    #return flask.render_template('index.jinja2', my_server=flask.request.url_root)
    return "Hello Dog"

@application.before_first_request
def pre_first_request():
    pass

application.run()