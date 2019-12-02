from odoo import models, fields
from . import image
import re

REGEX_IMAGE_FIELD = re.compile("image_(\d+)")

class ImageMixin(models.AbstractModel):
    _inherit = 'image.mixin'

    image_src_1920 = fields.Char("Image source")
    image_src_1024 = fields.Char("Image 1024 source")
    image_src_512 = fields.Char("Image 512 source")
    image_src_256 = fields.Char("Image 256 source")
    image_src_128 = fields.Char("Image 128 source")

    def create(self, vals):
        for val in vals:
            new_field_values = {}
            for key, value in val.items():
                match = REGEX_IMAGE_FIELD.match(key)
                if not match:
                    continue
                
                if not image.is_url(value):
                    continue
                
                width = match.group(1)
                new_field_values["image_src_{}".format(width)] = value
            val.update(new_field_values)

        return super(ImageMixin, self).create(vals)
        
