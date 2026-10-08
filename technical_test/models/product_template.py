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
    rop_status = fields.Selection(
        selection=[
            ("below", "ROP Products"),
            ("above", "Products > ROP"),
        ],
        string="ROP Status",
        compute="_compute_rop_status",
        search="_search_rop_status",
    )

    @api.depends("has_rop", "rop_count", "qty_available")
    def _compute_rop_status(self):
        for product in self:
            if not product.has_rop:
                product.rop_status = False
            elif product.qty_available <= product.rop_count:
                product.rop_status = "below"
            else:
                product.rop_status = "above"

    def _search_rop_status(self, operator, value):
        if operator != "=" or value not in ("below", "above"):
            return []

        products = self.search([
            ("has_rop", "=", True),
        ])

        if value == "below":
            products = products.filtered(
                lambda p: p.qty_available <= p.rop_count
            )
        else:
            products = products.filtered(
                lambda p: p.qty_available > p.rop_count
            )

        return [("id", "in", products.ids)]

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