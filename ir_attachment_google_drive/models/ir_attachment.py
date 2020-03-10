# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.tools import human_size
from odoo.tools.safe_eval import safe_eval
import logging
import requests
import base64
_logger = logging.getLogger(__name__)

PREFIX = "google_drive://"
TIMEOUT = 5

class IrAttachment(models.Model):

    _inherit = 'ir.attachment'

    def _get_google_drive_auth_header(self):
        return {'Authorization': "Bearer " + self.env['google.drive.config'].get_access_token()}

    # это нагло скопировано с ir_attachment_url
    @api.multi
    def _filter_protected_attachments(self):
        return self.filtered(
            lambda r: r.res_model not in ["ir.ui.view", "ir.ui.menu"]
            or not r.name.startswith("/web/content/")
            or not r.name.startswith("/web/static/")
        )

    def _inverse_datas(self):
        condition = self.env["ir.config_parameter"].sudo().get_param("google_drive.condition")

        if condition:
            condition = safe_eval(condition, mode="eval")
            our_records = self.sudo().search([("id", "in", self.ids)] + condition)
        else:
            our_records = self

        our_records = our_records._filter_protected_attachments()

        for attach in our_records:
            bin_value = base64.b64decode(attach.datas)
            fname = self._file_write_google_drive(bin_value)
            vals = {
                "file_size": len(bin_value),
                "checksum": self._compute_checksum(bin_value),
                "index_content": self._index(
                    bin_value, attach.datas_fname, attach.mimetype
                ),
                "store_fname": fname,
                "db_datas": False,
                "type": "binary",
            }
            super(IrAttachment, attach.sudo()).write(vals)

        return super(IrAttachment, self - our_records)._inverse_datas()

    def _file_read(self, fname, bin_size=False):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_read(fname, bin_size)

        print("read", fname)

        file_id = fname[len(PREFIX):]

        request_url = "https://www.googleapis.com/drive/v2/files/%s" % (file_id, )

        r = requests.get(request_url, headers=self._get_google_drive_auth_header(), timeout=TIMEOUT)
        r.raise_for_status()

        if bin_size:
            return human_size(r.json()['fileSize'])
        else:
            r = requests.get(r.json()['downloadUrl'], headers=self._get_google_drive_auth_header(), timeout=TIMEOUT)
            r.raise_for_status()
            return base64.b64encode(r.content)

    def _file_write_google_drive(self, bin_value):
        r = requests.post("https://www.googleapis.com/upload/drive/v2/files?uploadType=media", headers=self._get_google_drive_auth_header(), data=bin_value)
        r.raise_for_status()
        print("write", r.json()['id'])
        return PREFIX + r.json()['id']

    def _file_delete(self, fname):
        if not fname.startswith(PREFIX):
            return super(IrAttachment, self)._file_delete(fname)

        file_id = fname[len(PREFIX):]

        r = requests.delete("https://www.googleapis.com/drive/v2/files/%s" % (file_id,), headers=self._get_google_drive_auth_header(), timeout=TIMEOUT)
        r.raise_for_status()
