import os
import configparser
import argparse
from urllib.parse import urlparse
import sys
import pathlib

from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename


# P By StackOverflow user https://stackoverflow.com/users/190597/unutbu
class VAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None):
        super(VAction, self).__init__(option_strings, dest, nargs, const,
                                      default, type, choices, required,
                                      help, metavar)
        self.values = 0

    def __call__(self, parser, args, values, option_string=None):
        # print('values: {v!r}'.format(v=values))
        if values is None:
            self.values += 1
        else:
            try:
                self.values = int(values)
            except ValueError:
                self.values = values.count('v') + 1
        setattr(args, self.dest, self.values)


application = Flask(__name__)

uploads_dir = "file:///tmp/"

# P validate the uploads location
save_url = urlparse(uploads_dir)
if save_url.scheme not in ('file'):
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
    if 'file' not in request.files:
        return "No file detected"
    file = request.files['file']

    if file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)

    if save_url.scheme == 'file':
        application.logger.debug(os.path.join(save_url.path, filename))
        file.save(os.path.join(save_url.path, filename))
    else:
        return "Can't save file. Uploads scheme [{}] unsupported".format(save_url.scheme)
    return "OK"


@application.before_first_request
def pre_first_request():
    pass
