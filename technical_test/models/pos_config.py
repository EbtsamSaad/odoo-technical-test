from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    auto_invoice_cash_now = fields.Boolean(
        string="Auto Invoice on Cash Now",
        default=True,
        help=(
            "Automatically generate an accounting invoice "
            "when using the Cash Now button."
        ),
    )


