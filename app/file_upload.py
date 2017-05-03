import os
import StringIO
import zipfile
from flask import Flask, flash, redirect, request, Response, Blueprint, render_template

from werkzeug import secure_filename

import app

# Relevant directories
UPLOAD_FOLDER = 'data/'
RESULT_FOLDER = 'app/static/results/'

# Valid file extensions
ALLOWED_EXTENSIONS = set(['txt', 'csv'])

# Fields from web interface
FIELDS = ['mode', 'voi', 'stores', 'store_col',
            'time_col', 'title', 'yaxis', 'time_int']

# Five number summary fields
DENS_PLT_SUMMARY = ['minimum', 'maximum', 'median',
            'mean', 'q1', 'q3']

# Demo mode
DEMO = True

f_uploader = Blueprint('file_upload', __name__)

# Determine if file has valid extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Order configuration fields
def order_config(c, fields):
    config = []
    for f in fields:
        config.append(c[f])
    return config

# Write input to configuration file
def write_config(fname, entries, fields):
    data = order_config(entries, fields)
    with open(fname, 'w') as f:
        for d in data:
            f.write(d)
            f.write('\n')

# Read five number summary from R script
def read_num_summary(fname):
    with open(fname, 'r') as f:
        count = 0
        keys = []
        vals = []
        for line in f:
            line = line.strip()
            temp = line.split()
            temp = [x.strip('"') for x in temp]
            if not count:
                keys = temp
            else:
                vals = temp[1:]
            count += 1
    return dict(zip(keys, vals))

# Return list of five number summary
def get_num_sum(fname):
    results = read_num_summary(fname)
    output = []
    for num in DENS_PLT_SUMMARY:
        output.append('%s: %s' % (num, results[num]))
    return output

# Read regression summary from R script
def read_reg_summary(fname):
    with open(fname, 'r') as f:
        count = 0
        all_lines = []
        for line in f:
            line = line.strip()
            temp = line.split()
            temp = [x.strip('"') for x in temp]
            if not count:
                all_lines.append(temp)
            else:
                all_lines.append(temp[1:])
            count += 1
        return all_lines

# Return list of regression summary
def get_reg_sum(fname):
    results = read_reg_summary(fname)
    output = []
    for r in results:
        output.append(' '.join(r))
    return output

# Handle incoming requests
@f_uploader.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # If user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Check if file is valid and save configuration
        config = ''
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            config = os.path.join(UPLOAD_FOLDER, filename)+'.config'
            write_config(config, request.form, FIELDS)
        # Call R code
        if not DEMO:
            subprocess.call (['/usr/bin/Rscript', '--vanilla', 'MyrScript.r', config])
            output_name = RESULT_FOLDER+filename
            result_text = get_reg_sum(output_name+'.results.txt')
            return render_template('index.html',
                result_image=output_name+'.results.png',
                result_text=result_text)
        else:
            if request.form['mode'] == 'reg':
                result_text = get_reg_sum(RESULT_FOLDER+'Regression.txt')
                return render_template('index.html',
                    result_image='/static/image/Regression.png',
                    result_text=result_text)
            else:
                result_text = get_num_sum(RESULT_FOLDER+'5numbersummary.txt')
                if request.form['mode'] == 'den':
                    return render_template('index.html',
                            result_image='/static/image/Density.png',
                            result_text=result_text)
                else:
                    return render_template('index.html',
                            result_image='/static/image/Dot.png',
                            result_text=result_text)

    elif request.method == 'GET':
        # If download
        if 'dl' in request.args:
            return result_download(request.args['dl'])
        else:
            return render_template('index.html')

# Download result plot and summary
def result_download(fname):
    if not fname:
        raise InvalidUsage("", status_code=400)

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # Zip compressor
    added_fn = []
    zf = zipfile.ZipFile(s, 'w')
    temp = fname.rsplit('.', 1)[0].rsplit('/', 1)[1]

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
