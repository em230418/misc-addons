# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from . import image


class ProductTemplate(models.AbstractModel):
    _inherit = 'product.template'

    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for template in self:
            if image.is_url(template.image_1920):
                # we just assume that image links zoomed image
                template.can_image_1024_be_zoomed = True
            else:
                template.can_image_1024_be_zoomed = template.image_1920 and tools.is_image_size_above(template.image_1920, template.image_1024)
