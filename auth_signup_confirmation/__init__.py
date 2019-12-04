
from . import controllers
from odoo import api, SUPERUSER_ID


def init_auth(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    icp = env['ir.config_parameter']

    # previous allow_uninvited was taken away
    # https://github.com/odoo/odoo/commit/a18bd499acf518f070318aeabd81f8eb94faad01#diff-fcbac2d350904701dc8d0139c7e0d056
    icp.set_param('auth_signup.invitation_scope', 'b2b')
