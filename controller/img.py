import os
import sys
import random
import string
import time
from PIL import Image

import tornado.web
import tornado.escape

from tornado.log import app_log

from controller.base import *

class UploadHandler(BaseHandler):
    def post(self):
        result = {'success': True}
        dirname = '/home/yli/uploads'
        if self.request.files:
            try:
                upload_img = self.request.files['postfile'][0]
                rawname = upload_img['filename']
                destname = '%d%s' % (time.time(), ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6)))
                thumbname = 'thumb_%s' % destname
                path = '%s/%s/pics/' % (dirname, self.current_user.user_id)
                if not os.path.exists(path):
                    os.makedirs(path)
                extension = os.path.splitext(rawname)[1]
                destname = ''.join((path, destname, extension))
                output_img = open(destname, 'w')
                output_img.write(upload_img['body'])
                output_img.close()

                oimg = Image.open(destname)
                oimg.thumbnail((160, 160), resample=1)
                thumbname = ''.join((path, thumbname, extension))
                oimg.save(thumbname)
                result['thumbname'] = thumbname[len(dirname):]
                result['filename'] = destname[len(dirname):]
            except Exception, e:
                app_log.error(str(e))
                result['success'] = False
                result['err_info'] = 'File type unsupported'
        else:
            result['success'] = False
            result['err_info'] = 'No upload file'
        self.write(tornado.escape.json_encode(result))

class FileHandler(BaseHandler):
    def get(self, filename):
        filename = '/home/yli/uploads/' + filename
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                self.write(file.read())
        else:
            self.redirect('/static/image_not_found.png')

class DeleteHandler(BaseHandler):
    def post(self):
        filename = self.get_argument('filename')
        result = {'success': True}
        try:
            path = 'uploads/%s/pics/' % self.current_user.user_id
            os.remove(path + filename)
            if filename.startswith('thumb_'):
                orname = filename[6:]
            else:
                orname = 'thumb_' + filename
            os.remove(path + orname)
        except:
            result = {'success': False, 'err_info': 'Delete file failed'}
        self.write(tornado.escape.json_encode(result))

