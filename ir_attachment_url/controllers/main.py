import base64

import requests

from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route("/web/convert_url_to_base64", type="http", auth="user")
    def convert_url_to_base64(self, url, **kw):
        r = requests.get(url, timeout=5, stream=True)
        r.raise_for_status()
        response = request.make_response(
            base64.b64encode(r.content), [("Content-Type", "text/plain")]
        )
        return response
