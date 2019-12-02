# Copyright 2017 Dinar Gabbasov <https://www.it-projects.info/team/GabbasovDinar>
# Copyright 2018 Rafis Bikbov <https://www.it-projects.info/team/RafiZz>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import fields
import mimetypes
import requests

from odoo.tools.mimetypes import guess_mimetype
from . import image
from .image_mixin import REGEX_IMAGE_FIELD

# TODO: anything to rewrite?

def get_mimetype_and_optional_content_by_url(url):
    mimetype = mimetypes.guess_type(url)[0]
    content = None

    # head request for content-type header getting
    if not mimetype:
        with requests.head(url, timeout=5) as r:
            mimetype = getattr(r, 'headers', {}).get('Content-Type')

    index_content = mimetype and mimetype.split('/')[0]
    if not mimetype or index_content == 'text':
        with requests.get(url, timeout=5) as r:
            content = getattr(r, 'content')
            if not mimetype and content:
                mimetype = guess_mimetype(content)

    return mimetype, content


class Binary(fields.Binary):

    def create(self, record_values):
        assert self.attachment
        if not record_values:
            return
        # create the attachments that store the values
        env = record_values[0][0].env

        with env.norecompute():
            env['ir.attachment'].sudo().with_context(
                binary_field_real_user=env.user,
            ).create([{
                    'name': self.name,
                    'res_model': self.model_name,
                    'res_field': self.name,
                    'res_id': record.id,
                    'type': 'url',
                    'url': value,
                }
                for record, value in filter(lambda x: image.is_url(x[1]), record_values)
                if value
            ])
        super(Binary, self).create(list(filter(lambda x: not image.is_url(x[1]), record_values)))

    def convert_to_cache(self, value, record, validate=True):
        if image.is_url(value):
            return value
        return super(Binary, self).convert_to_cache(value, record, validate)

    def write(self, records, value):
        if not self.attachment:
            return super().write(records, value)

        # discard recomputation of self on records
        records.env.remove_to_compute(self, records)

        # update the cache, and discard the records that are not modified
        cache = records.env.cache
        cache_value = self.convert_to_cache(value, records)
        records = cache.get_records_different_from(records, self, cache_value)
        if not records:
            return records
        if self.store:
            # determine records that are known to be not null
            not_null = cache.get_records_different_from(records, self, None)

        cache.update(records, self, [cache_value] * len(records))

        if not image.is_url(value):
            return super(Binary, self).write(records, value)

        # retrieve the attachments that store the values, and adapt them
        if self.store:
            atts = records.env['ir.attachment'].sudo()
            if not_null:
                atts = atts.search([
                    ('res_model', '=', self.model_name),
                    ('res_field', '=', self.name),
                    ('res_id', 'in', records.ids),
                ])
            if value:
                # update the existing attachments
                atts_records = records.browse(atts.mapped('res_id'))
                # create the missing attachments
                missing = (records - atts_records).filtered('id')
                if missing:
                    atts.create([{
                            'name': self.name,
                            'res_model': record._name,
                            'res_field': self.name,
                            'res_id': record.id,
                            'type': 'url',
                            'url': value,
                        }
                        for record in missing
                    ])
            else:
                atts.unlink()

        return records


    def compute_value(self, records):
        """
        Compute image_* value from exising image_src_* values, if present
        """
        match = REGEX_IMAGE_FIELD.match(self.name)
        if not match:
            return super(Binary, self).compute_value(records)

        w = match.group(1)
        src_field = 'image_src_' + w
        records_with_image_src = records.filtered(lambda r: src_field in r and r[src_field])

        for record in records_with_image_src:
            record['image_' + w] = record[src_field]

        super(Binary, self).compute_value(records - records_with_image_src)


fields.Binary = Binary
fields.Image.__bases__ = (Binary,)
