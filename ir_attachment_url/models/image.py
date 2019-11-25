# Copyright 2017 Dinar Gabbasov <https://www.it-projects.info/team/GabbasovDinar>
# Copyright 2018 Rafis Bikbov <https://www.it-projects.info/team/RafiZz>
# Copyright 2019 Eugene Molotov <https://www.it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import tools
import re


super_image_process = tools.image_process


def is_url(value):
    if value:
        return isinstance(value, str) and re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", value)


def image_process(base64_source, size=(0, 0), verify_resolution=False, quality=0, crop=None, colorize=False, output_format=""):
    source_for_check = base64_source.decode("utf-8") if isinstance(base64_source, bytes) else base64_source)
    if is_url(source_for_check):
        return source_for_check
    return super_image_process(base64_source, size, verify_resolution, quality, crop, colorize, output_format)


tools.image_process = image_process
