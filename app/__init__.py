from flask import Flask
from flask import jsonify
# from error_handler import InvalidUsage
# from flask.ext.cors import CORS

# Define the WSGI application object                                                                                                                                                 
app = Flask(__name__)

# Cross Origin Resource Sharing(CORS) is required by SWAGGER API                                                                                                                     
# CORS(app)

# constants are used for APP configuration                                                                                                                                           
ALLOWED_EXTENSIONS = set(['xml', 'txt', 'zip'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['UPLOAD_FOLDER'] = '.'

from file_upload import f_uploader
app.register_blueprint(f_uploader)


# # HTTP error handling                                                                                                                                                                
# @app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response

# get elisa_ie root path                                                                                                                                                             
# import os