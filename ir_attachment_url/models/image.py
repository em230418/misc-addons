# Copyright 2017 Dinar Gabbasov <https://www.it-projects.info/team/GabbasovDinar>
# Copyright 2018 Rafis Bikbov <https://www.it-projects.info/team/RafiZz>
# Copyright 2019 Eugene Molotov <https://www.it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import odoo
from odoo import tools
import re


super_image_process = tools.image_process
super_is_image_size_above = tools.is_image_size_above


def is_url(value):
    if value:
        return isinstance(value, str) and re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", value)


def image_process(base64_source, size=(0, 0), verify_resolution=False, quality=0, crop=None, colorize=False, output_format=""):
    source_for_check = base64_source.decode("utf-8") if isinstance(base64_source, bytes) else base64_source
    if source_for_check:
        print(source_for_check[:100])
    if is_url(source_for_check):
        return source_for_check
    return super_image_process(base64_source, size, verify_resolution, quality, crop, colorize, output_format)


# it is used at least here:
# https://github.com/odoo/odoo/blob/3f17dd36e8369c21e55009e5492438cb9f9ea53d/addons/product/models/product_template.py#L163
def is_image_size_above(base64_source_1, base64_source_2):
    if is_url(base64_source_1) or is_url(base64_source_2):
        return False
    return super_is_image_size_above(base64_source_1, base64_source_2)


tools.is_image_size_above = is_image_size_above
tools.image_process = image_process
odoo.fields.image_process = image_process
