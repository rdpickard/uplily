import os
import hashlib
import json

import flask
from werkzeug.utils import secure_filename
import boto3

application = flask.Flask(__name__)

uploads_dir = "/tmp/uplily/"
if not os.path.exists(uploads_dir):
    os.mkdir(uploads_dir)


# P Gently stolen from https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
def md5_a_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@application.route('/ul/', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in flask.request.files:
        return "No file detected"
    file = flask.request.files['file']

    if file.filename == '':
        return "No file selected"

    filename = secure_filename(file.filename)

    application.logger.debug(os.path.join(uploads_dir, filename))
    file.save(os.path.join(uploads_dir, filename))

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
    uploaded_files = dict()

    for filename in [f for f in os.listdir(uploads_dir) if os.path.isfile(uploads_dir+"/"+f)]:
        uploaded_files[filename] = {"download_url": "{}dl/{}".format(flask.request.url_root, filename),
                                    "locale": "Local FS",
                                    "md5_hash": md5_a_file(os.path.join(uploads_dir, filename)),
                                    "file_size_in_bytes": os.stat(os.path.join(uploads_dir, filename)).st_size}

    return flask.render_template('index.jinja2',
                                 my_server=flask.request.url_root,
                                 uploaded_files_dir=uploads_dir,
                                 uploaded_files_list=uploaded_files)


@application.route('/dl/<string:filename>')
def download_file(filename):

    if filename not in os.listdir(uploads_dir):
        flask.abort(404)
    else:
        return flask.send_from_directory(uploads_dir, filename, as_attachment=True)


@application.route('/sign_s3/')
def sign_s3():
    # From Heroku documentation https://devcenter.heroku.com/articles/s3-upload-python

    if not all(map(lambda ev: os.environ.get(ev) is not None,
                   ['S3_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'])):
        content = {'error': 'S3 environment variables not set up'}
        return content, 501

    s3_bucket = os.environ.get('S3_BUCKET')

    file_name = flask.request.args.get('file_name')
    file_type = flask.request.args.get('file_type')

    s3 = boto3.client('s3')

    presigned_post = s3.generate_presigned_post(
        Bucket=s3_bucket,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type}
        ],
        ExpiresIn=3600
    )

    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (s3_bucket, file_name)
    })


@application.before_first_request
def pre_first_request():
    pass


if __name__ == "__main__":
    application.run()
