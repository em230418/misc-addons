# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

class Main(http.Controller):
    @http.route('/stream/stock_camera/<int:camera_id>', type='http', auth='user')  # TODO: auth MUST NOT BE PUBLIC
    def camera_stream(self, camera_id, *args, **kwargs):
        camera = request.env['stock.camera.config'].browse(camera_id)  # TODO: настроить права
        if not camera:
            # TODO: return as a picture
            return "Camera not found"

        # TODO: для избежания memory leak попробуй вернуть https://github.com/odoo/odoo/blob/13.0/odoo/http.py#L1454
        # типа вот так: https://gist.github.com/kgaughan/6021407#file-demo-py-L58-L62
        return http.Response(gen(camera.camera_instance()), mimetype='multipart/x-mixed-replace; boundary=frame', direct_passthrough=True)
