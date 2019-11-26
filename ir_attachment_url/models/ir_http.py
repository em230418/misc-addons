# Copyright 2016-2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2017 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import mimetypes
import base64
import hashlib
import re
import os

from odoo import models
from odoo.exceptions import AccessError
from odoo.tools.mimetypes import guess_mimetype
from odoo.http import request, STATIC_CACHE
from odoo.modules.module import get_resource_path, get_module_path
from odoo.tools import pycompat, consteq


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _find_field_attachment(cls, env, m, f, res_id):
        domain = [
            ('res_model', '=', m),
            ('res_field', '=', f),
            ('res_id', '=', res_id),
            ('type', '=', 'url'),
        ]
        return env['ir.attachment'].sudo().search(domain)

    @classmethod
    def find_field_attachment(cls, env, model, field, obj):
        is_attachment = env[model]._fields[field].attachment
        is_product = model == 'product.product' and field.startswith('image')
        if not (is_attachment or is_product):
            return None

        att = cls._find_field_attachment(env, model, field, obj.id)

        if not att and model == 'product.product':
            # Special case. Product.product's image are computed and
            # use product.template's image in most cases. But due to
            # this computation odoo pass binary data (by downloading it
            # from s3) instead of url. So, make a workaround for it
            att = cls._find_field_attachment(env, 'product.template', field, obj.product_tmpl_id.id)
        return att

    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None):  # pylint: disable=redefined-builtin

        record, status = self._get_record_and_check(xmlid=xmlid, model=model, id=id, field=field, access_token=access_token)

        if not record:
            return (status or 404, [], None)

        content, headers, status = None, [], None

        if record._name == 'ir.attachment':
            status, content, filename, mimetype, filehash = self._binary_ir_attachment_redirect_content(record, default_mimetype=default_mimetype)
        # begin redefined part
        if not content:
            att = self.find_field_attachment(self.env, model, field, record)
            if att:
                content = att.url
                status = 301
                mimetype = att.mimetype
        # end redefined part
        if not content:
            status, content, filename, mimetype, filehash = self._binary_record_content(
                record, field=field, filename=filename, filename_field=filename_field,
                default_mimetype='application/octet-stream')

        status, headers, content = self._binary_set_headers(
            status, content, filename, mimetype, unique, filehash=filehash, download=download)

        return status, headers, content
