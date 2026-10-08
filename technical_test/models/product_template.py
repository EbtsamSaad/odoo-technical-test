from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    has_rop = fields.Boolean(
        string="Has ROP",
        default=False,
    )

    rop_count = fields.Integer(
        string="ROP Count",
        default=0,
    )

    same_rop_product_count = fields.Integer(
        string="Products with Same ROP",
        compute="_compute_same_rop_product_count",
    )

    @api.depends("has_rop", "rop_count")
    def _compute_same_rop_product_count(self):
        ProductTemplate = self.env["product.template"]

        for product in self:
            if not product.has_rop or product.rop_count <= 0:
                product.same_rop_product_count = 0
                continue

            domain = [
                ("has_rop", "=", True),
                ("rop_count", "=", product.rop_count),
            ]

            if product._origin.id:
                domain.append(("id", "!=", product._origin.id))

            product.same_rop_product_count = ProductTemplate.search_count(domain)

    @api.constrains("rop_count")
    def _check_rop_count(self):
        for product in self:
            if product.rop_count < 0:
                raise ValidationError(
                    "ROP Count cannot be negative."
                )

    def action_view_same_rop_products(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Products with Same ROP",
            "res_model": "product.template",
            "view_mode": "kanban,tree,form",
            "domain": [
                ("id", "!=", self.id),
                ("has_rop", "=", True),
                ("rop_count", "=", self.rop_count),
            ],
        }