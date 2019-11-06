# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockCameraConfig(models.Model):

    _name = 'stock.camera.config'
    _description = 'Camera configuration'
