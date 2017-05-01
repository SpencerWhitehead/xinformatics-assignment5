from flask import Flask
from flask import jsonify

# Define the WSGI application object                                                                                                                                                 
app = Flask(__name__)

# constants are used for APP configuration                                                                                                                                           
ALLOWED_EXTENSIONS = set(['csv', 'txt'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

from file_upload import f_uploader
app.register_blueprint(f_uploader)