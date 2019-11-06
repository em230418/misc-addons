# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route('/hello/world', auth='public')
    def index(self, **kw):
        return "Hello, world"
