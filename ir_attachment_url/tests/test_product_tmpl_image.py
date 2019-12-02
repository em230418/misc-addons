# Copyright 2019 Rafis Bikbov <https://it-projects.info/team/RafiZz>
# Copyright 2019 Alexandr Kolushov <https://it-projects.info/team/KolushovAlexandr>
# Copyright 2019 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, conf
from odoo.tests.common import HttpCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestProductTmplImage(HttpCase):

    def _get_original_image_url(self, px=1024):
        return 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Gullfoss%2C_an_iconic_waterfall_of_Iceland.jpg/{}px-Gullfoss%2C_an_iconic_waterfall_of_Iceland.jpg'\
            .format(px)

    def _get_odoo_image_url(self, model, record_id, field):
        return '/web/image?model={}&id={}&field={}'.format(model, record_id, field)

    def test_getting_product_variant_image_fields_urls(self):
        assert 'ir_attachment_url' in conf.server_wide_modules, "ir_attachment_url is not in server_wide_modules. Please add it via --load parameter"

        env = api.Environment(self.registry.test_cr, self.uid, {})

        env['ir.config_parameter'].set_param('ir_attachment_url.storage', 'url')

        # 12.0 -> 13.0 porting notes
        # 1. image fields are renamed: https://github.com/odoo/odoo/commit/58a2ffa26f1a3b0f9630ce16d11b758d18e20a21
        # 2. image_64 (previously a.k.a image_small) is removed: https://github.com/odoo/odoo/commit/b6288e54461426d7aac6cfc549cee3e90309a093

        dummy_attr = self.env['product.attribute'].create({'name': 'Dummy'})
        dummy_attr_value = self.env['product.attribute.value'].create({'name': 'Dummy value', 'attribute_id': dummy_attr.id})

        product_tmpl = env['product.template'].create({
            'name': 'Test template',
            'image_1920': self._get_original_image_url(1920),
            'image_1024': self._get_original_image_url(1024),
            'image_512': self._get_original_image_url(512),
            'image_256': self._get_original_image_url(256),
            'image_128': self._get_original_image_url(128),
            'attribute_line_ids': [(0, 0, {
                'attribute_id': dummy_attr.id,
                'value_ids': [(4, dummy_attr_value.id)],
            })]
        })

        product_product = env['product.product'].create({
            'name': 'Test product',
            'product_tmpl_id': product_tmpl.id
        })

        odoo_image_url_1920 = self._get_odoo_image_url('product.product', product_product.id, 'image_1920')
        odoo_image_url_1024 = self._get_odoo_image_url('product.product', product_product.id, 'image_1024')
        odoo_image_url_512 = self._get_odoo_image_url('product.product', product_product.id, 'image_512')
        odoo_image_url_256 = self._get_odoo_image_url('product.product', product_product.id, 'image_256')
        odoo_image_url_128 = self._get_odoo_image_url('product.product', product_product.id, 'image_128')

        product_tmpl_image_attachment_1920 = env['ir.http'].find_field_attachment(env, 'product.template', 'image_1920', product_tmpl)
        product_tmpl_image_attachment_1024 = env['ir.http'].find_field_attachment(env, 'product.template', 'image_1024', product_tmpl)
        product_tmpl_image_attachment_512 = env['ir.http'].find_field_attachment(env, 'product.template', 'image_512', product_tmpl)
        product_tmpl_image_attachment_256 = env['ir.http'].find_field_attachment(env, 'product.template', 'image_256', product_tmpl)
        product_tmpl_image_attachment_128 = env['ir.http'].find_field_attachment(env, 'product.template', 'image_128', product_tmpl)

        self.assertTrue(len(product_tmpl_image_attachment_1920) == 1)
        self.assertTrue(len(product_tmpl_image_attachment_1024) == 1)
        self.assertTrue(len(product_tmpl_image_attachment_512) == 1)
        self.assertTrue(len(product_tmpl_image_attachment_256) == 1)
        self.assertTrue(len(product_tmpl_image_attachment_128) == 1)

        self.authenticate('demo', 'demo')

        self.assertEqual(self.url_open(odoo_image_url_1920).url, product_tmpl_image_attachment_1920.url)
        self.assertEqual(self.url_open(odoo_image_url_1024).url, product_tmpl_image_attachment_1024.url)
        self.assertEqual(self.url_open(odoo_image_url_512).url, product_tmpl_image_attachment_512.url)
        self.assertEqual(self.url_open(odoo_image_url_256).url, product_tmpl_image_attachment_256.url)
        self.assertEqual(self.url_open(odoo_image_url_128).url, product_tmpl_image_attachment_128.url)
