import logging

from odoo.tests.common import HttpCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestDataGet(HttpCase):

    def test_data_get(self):
        test_attachment = self.env.ref('ir_attachment_url.test_url_attachment')
        self.env['ir.attachment'].search_read([("id", "=", test_attachment.id)], ['id', 'datas'])

    def test_open_url(self):
        # TODO: что тут вообще проверять?
        user_demo = self.env.ref('base.user_demo')
        url = '/web/image?model=res.users&id={}&field=image_512'.format(user_demo.id)

        self.url_open(url)
