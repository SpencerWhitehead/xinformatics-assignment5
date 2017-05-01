import os
# from flask import Flask, request, redirect, url_for
from flask import Flask, redirect, request, Response, Blueprint, render_template, url_for, send_file

from werkzeug import secure_filename

import app

# UPLOAD_FOLDER = '/tmp/'
UPLOAD_FOLDER = 'data/'
RESULT_FOLDER = 'results/'

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
        # print request.form
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('index'))
            write_config(file.filename+'.config', request.form, FIELDS)
        # Call R code
        # return send_from_directory('./results/')
        # return render_template('sales_analysis.html',
        #         result_image=os.path.join(RESULT_FOLDER, file.filename+'.results.png'))
        # return send_file(os.path.join(RESULT_FOLDER, file.filename+'.results.png'),
        #             as_attachment=True, attachment_filename='myfile.jpg')
        # return send_file(RESULT_FOLDER+'results.png',
        #             as_attachment=True)
        return send_file('results.png',
                    as_attachment=True)

    elif request.method == 'GET':
        print 'GETTING HERE'
        return render_template('sales_analysis.html')

@f_uploader.route('/<filename>', methods=['GET', 'POST'])
def display_image(filename):
    print 'HERE'
    return send_from_directory('.', filename)
    # return render_template('sales_analysis.html',
                # result_image=os.path.join(RESULT_FOLDER, filename))


# @f_uploader('/show/<filename>')
    # f_list = ['None']
    # if len(os.listdir(UPLOAD_FOLDER)) > 0:
    #     f_list = os.listdir(UPLOAD_FOLDER)

    # return render_template('sales_analysis.html', uploaded="\n".join(f_list))

# @f_uploader.route("/", methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(UPLOAD_FOLDER, filename))
#             # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             # return redirect(url_for('index'))
#     return """
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form action="" method=post enctype=multipart/form-data>
#       <p><input type=file name=file>
#          <input type=submit value=Upload>
#     </form>
#     <p>%s</p>
#     """ % "<br>".join(os.listdir(UPLOAD_FOLDER))


@f_uploader.route("/plot_download/<name>", methods=["GET"])
def ne_annotation_download(name):
    if not name:
        raise InvalidUsage("", status_code=400)

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # Zip compressor
    zf = zipfile.ZipFile(s, "w")

    added_fn = []

    for root, dirs, files in os.walk(os.path.join(elisa_ie_root, 'data/demo/user_data/annotation_ne')):
        for fn in files:
            if fn in ['.DS_Store', '.gitignore']:
                continue
            if name == "<all>":
                zf.write(os.path.join(root, fn), fn)
                added_fn.append(fn)
            elif fn.split('_')[1] == name:
                zf.write(os.path.join(root, fn), fn)
                added_fn.append(fn)

    zf.close()

    if not added_fn:
        raise InvalidUsage('didn\'t find annotations for %s' % name, status_code=404)

    return Response(s.getvalue(),
                    mimetype='application/x-zip-compressed',
                    headers={"Content-disposition": 'attachment;filename=annotation_ne.zip'})


# @f_uploader.route("/", methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('index'))
#     return """
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form action="" method=post enctype=multipart/form-data>
#       <p><input type=file name=file>
#          <input type=submit value=Upload>
#     </form>
#     <p>%s</p>
#     """ % "<br>".join(os.listdir(f_uploader.config['UPLOAD_FOLDER']))