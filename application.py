import os
import hashlib
import json

import flask
from werkzeug.utils import secure_filename
import boto3

application = flask.Flask(__name__)
application.config['TEMPLATES_AUTO_RELOAD'] = True

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


def uploaded_files_on_local_fs():
    uploaded_files = {}
    for filename in [f for f in os.listdir(uploads_dir) if os.path.isfile(uploads_dir+"/"+f)]:
        uploaded_files[filename] = {"download_url": "{}dl/{}".format(flask.request.url_root, filename),
                                    "locale": "Local FS",
                                    "md5_hash": md5_a_file(os.path.join(uploads_dir, filename)),
                                    "file_size_in_bytes": os.stat(os.path.join(uploads_dir, filename)).st_size}
    return uploaded_files


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except Exception as e:
        application.logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def list_files_in_s3_bucket():

    s3_files = {}
    s3_enabled = all(map(lambda ev: os.environ.get(ev) is not None,
                   ['S3_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']))
    s3_bucket_name = os.environ.get('S3_BUCKET')
    s3 = boto3.resource("s3")
    s3_bucket = s3.Bucket(s3_bucket_name)

    for my_bucket_object in s3_bucket.objects.all():
        s3_files[my_bucket_object.key] = {"download_url": create_presigned_url(s3_bucket_name, my_bucket_object.key),
                                          "locale": "S3",
                                          "md5_hash": my_bucket_object.e_tag[1 :-1],
                                          "file_size_in_bytes":my_bucket_object.size}

    return s3_files

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
        return flask.redirect("/?message_ok=Upload%20OK", code=302)
    else:
        return "OK"


@application.route("/available_files")
def available_files():
    """
    Returns a JSON object of the files available to download
    :return:
    """
    s3_files = {}
    s3_enabled = all(map(lambda ev: os.environ.get(ev) is not None,
                   ['S3_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']))

    if s3_enabled:
        s3_files = list_files_in_s3_bucket()

    local_files = uploaded_files_on_local_fs()

    local_files.update(s3_files)
    return flask.jsonify(local_files)


@application.route('/')
def index():
    """
    Renders the 'index' page
    :return:
    """

    s3_enabled = all(map(lambda ev: os.environ.get(ev) is not None,
                   ['S3_BUCKET', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']))

    return flask.render_template('index.jinja2',
                                 my_server=flask.request.url_root,
                                 uploaded_files_dir=uploads_dir,
                                 uploaded_files_list=uploaded_files_on_local_fs(),
                                 s3_enabled=s3_enabled,
                                 message_ok=flask.request.args.get("message_ok", None),
                                 message_err=flask.request.args.get("message_err", None))


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
        Fields={"acl": "private", "Content-Type": file_type},
        Conditions=[
            {"acl": "private"},
            {"Content-Type": file_type}
        ],
        ExpiresIn=3600
    )

    return json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (s3_bucket, file_name)
    })


@application.route('/css/<path:path>')
def send_css(path):
    return flask.send_from_directory('staticfiles/css', path)


@application.route('/js/<path:path>')
def send_js(path):
    return flask.send_from_directory('staticfiles/js', path)


@application.route('/fonts/<path:path>')
def send_font(path):
    return flask.send_from_directory('staticfiles/fonts', path)


@application.route('/media/<path:path>')
def send_media(path):
    return flask.send_from_directory('staticfiles/media', path)


@application.before_first_request
def pre_first_request():
    pass


if __name__ == "__main__":
    application.run()
