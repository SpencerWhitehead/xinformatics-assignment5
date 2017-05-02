import os,sys

from app import app

if __name__=='__main__':
    app.run('0.0.0.0', port=3300, threaded=True)