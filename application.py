import os
from urllib.parse import urlparse
import sys
import hashlib

import flask
from werkzeug.utils import secure_filename


application = flask.Flask(__name__)

uploaded_files = dict()

uploads_dir = "file:///tmp/"


# P Gently stolen from https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5_a_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


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


@application.route('/ul/', methods=['POST'])
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
        uploaded_files[filename] = {"download_url": "{}dl/{}".format(flask.request.url_root, filename),
                                    "locale": "Local FS",
                                    "md5_hash": md5_a_file(os.path.join(save_url.path, filename)),
                                    "file_size_in_bytes": os.stat(os.path.join(save_url.path, filename)).st_size}
    else:
        return "Can't save file. Uploads scheme [{}] unsupported".format(save_url.scheme)

    if flask.request.args.get("browser_upload", False):
        return flask.redirect("/", code=302)
    else:
        return "OK"


@application.route('/')
def index():
    """
    Renders the 'index' page
    :return:
    """
    return flask.render_template('index.jinja2',
                                 my_server=flask.request.url_root, uploaded_files_list=uploaded_files)


@application.route('/dl/<string:filename>')
def download_file(filename):

    if filename not in uploaded_files:
        flask.abort(404)
    else:
        return flask.send_from_directory(save_url.path, filename, as_attachment=True)


@application.before_first_request
def pre_first_request():
    pass


if __name__ == "__main__":
    application.run()
