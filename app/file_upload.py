import os
import StringIO
import zipfile
# from flask import Flask, request, redirect, url_for
from flask import Flask, redirect, request, Response, Blueprint, render_template, url_for, send_file

from werkzeug import secure_filename

import app

# UPLOAD_FOLDER = '/tmp/'
UPLOAD_FOLDER = 'data/'
RESULT_FOLDER = 'app/static/results/'

ALLOWED_EXTENSIONS = set(['txt', 'csv'])
FIELDS = ['mode', 'voi', 'stores', 'store_col',
            'time_col', 'title', 'yaxis', 'time_int']

# app = Flask(__name__)
f_uploader = Blueprint('file_upload', __name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def order_config(c, fields):
    config = []
    for f in fields:
        config.append(c[f])
    return config

def write_config(fname, entries, fields):
    data = order_config(entries, fields)
    with open(fname, 'w') as f:
        for d in data:
            f.write(d)
            f.write('\n')

@f_uploader.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            write_config(file.filename+'.config', request.form, FIELDS)
        # Call R code
        # subprocess.call (['/usr/bin/Rscript', '--vanilla', 'MyrScript.r', 'data/config'])
        # return render_template('ALTindex.html',
        #         result_image='/static/image/Density.png')
        return render_template('ALTindex.html',
                result_image='/static/results/%s' % (file.filename+'.results.png'))

    elif request.method == 'GET':
        print 'GETTING HERE'
        print request.args
        if 'dl' in request.args:
            return result_download(request.args['dl'])
        else:
            return render_template('ALTindex.html')
        # return render_template('sales_analysis.html')


def result_download(fname):
    if not fname:
        raise InvalidUsage("", status_code=400)

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # Zip compressor
    added_fn = []
    zf = zipfile.ZipFile(s, 'w')
    temp = fname.rsplit('.', 1)[0].rsplit('/', 1)[1]

    print temp
    for fn in os.listdir(RESULT_FOLDER):
        if temp in fn:
            zf.write(os.path.join(RESULT_FOLDER, fn), fn)
            added_fn.append(temp)

    zf.close()
    if not len(added_fn):
        raise InvalidUsage('didn\'t find annotations for %s' % fname, status_code=404)

    return Response(s.getvalue(),
                    mimetype='application/x-zip-compressed',
                    headers={"Content-disposition": 'attachment;filename=results.zip'})
