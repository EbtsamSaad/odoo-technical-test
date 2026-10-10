from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden


class WebsiteROPController(http.Controller):

    @http.route(
        "/shop/rop",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def shop_rop(self, **kwargs):
        user = request.env.user
        if not (
            user.has_group("base.group_system")
            or user.has_group("stock.group_stock_manager")
            or user.has_group("stock.group_stock_user")
        ):
            raise Forbidden()

        products = request.env["product.template"].search([
            ("sale_ok", "=", True),
            ("is_published", "=", True),
        ])
        low_stock_products = products.filtered(
            lambda product: product.qty_available < 5
        )
        return request.render(
            "technical_test.website_rop_products",
            {
                "products": low_stock_products,
            },
        )