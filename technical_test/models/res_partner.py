from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_admin_partner_id(self):
        admin_user = self.env.ref("base.user_admin", raise_if_not_found=False)
        if not admin_user or not admin_user.partner_id:
            return False

        return admin_user.partner_id.id