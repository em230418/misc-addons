# Copyright 2016-2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2017 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2016-2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).
import base64
import hashlib
import mimetypes
import os
import re

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def _find_field_attachment(self, m, f, res_id):
        domain = [
            ("res_model", "=", m),
            ("res_field", "=", f),
            ("res_id", "=", res_id),
            ("type", "=", "binary"),
            ("url", "!=", False),
        ]
        return (
            self.env["ir.attachment"]
            .sudo()
            .search_read(domain=domain, fields=["url", "mimetype", "checksum"], limit=1)
        )

    def find_field_attachment(self, model, field, obj):
        att = self._find_field_attachment(model, field, obj.id)

        if not att and model == "product.product":
            # Special case. Product.product's image are computed and
            # use product.template's image in most cases. But due to
            # this computation odoo pass binary data (by downloading it
            # from s3) instead of url. So, make a workaround for it
            att = self._find_field_attachment(
                "product.template", field, obj.product_tmpl_id.id
            )
        # Очередной гребаный костыль
        if not att and model == "res.users":
            att = self._find_field_attachment("res.partner", field, obj.partner_id.id)
        return att

    def _binary_record_content(self, record, **kw):
        model = record._name
        field = kw.get("field", "datas")
        res_id = record.id

        filename = kw.get("filename")
        mimetype = "mimetype" in record and record.mimetype or False
        content = None
        filehash = "checksum" in record and record["checksum"] or False

        field_def = record._fields[field]
        if field_def.type == "binary" and field_def.attachment:
            field_attachment = self.find_field_attachment(model, field, record)
            if field_attachment:
                mimetype = field_attachment[0]["mimetype"]
                content = field_attachment[0]["url"]
                filehash = field_attachment[0]["checksum"]
                return 301, content, filename, mimetype, filehash

        return super(IrHttp, self)._binary_record_content(record, **kw)
