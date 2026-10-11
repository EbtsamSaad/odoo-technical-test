import json
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden, BadRequest
from odoo.exceptions import UserError


class WebsiteROPController(http.Controller):

    def _check_rop_access(self):
        user = request.env.user
        if not (
                user.has_group("base.group_system")
                or user.has_group("stock.group_stock_manager")
                or user.has_group("stock.group_stock_user")
        ):
            raise Forbidden()

    @http.route(
        "/shop/rop",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def shop_rop(self, **kwargs):
        self._check_rop_access()

        products = request.env["product.product"].search([
            ("sale_ok", "=", True),
            ("type",     "=", "product"),  ])
        low_stock_products = products.filtered(
            lambda product: product.qty_available < 5
        )
        return request.render(
            "technical_test.website_rop_products",
            {
                "products": low_stock_products,
            },
        )

    @http.route(
        "/shop/rop/update_quantity",
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def update_rop_quantity(self, product_id, quantity, **kwargs):
        self._check_rop_access()
        user = request.env.user

        product = request.env["product.product"].browse(int(product_id)).exists()
        if not product:
            raise UserError("Product not found.")
        if product.detailed_type != "product":
            raise UserError("Only storable products can have their stock quantity adjusted.")

        # Use the warehouse's internal stock location.
        warehouse = request.env["stock.warehouse"].search([
            ("company_id", "=", request.env.company.id),
        ], limit=1)
        if not warehouse:
            raise UserError("No warehouse is configured for the current company.")
        location = warehouse.lot_stock_id
        print('location', location)
        quant = request.env["stock.quant"].search([
            ("product_id", "=", product.id),
            ("location_id", "=", location.id),
        ], limit=1)

        if quant:
            quant.inventory_quantity = quantity
        else:
            quant = request.env["stock.quant"].create({
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity": quantity,
            })

        quant.action_apply_inventory()

        # Notify other warehouse administrators.
        admin_group = request.env.ref("stock.group_stock_manager")
        admin_users = admin_group.users.filtered(
            lambda admin: admin.id != user.id and admin.active
        )

        for admin in admin_users:
            product.product_tmpl_id.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=admin.id,
                summary="ROP Product Quantity Updated",
                note=(
                    f"Product: {product.display_name}<br/>"
                    f"Updated Quantity: {quantity}<br/>"
                    f"Updated By: {user.name}"
                ),
            )

        return {
            "success": True,
            "product_id": product.id,
            "quantity": product.qty_available,
        }

    # Real-time ROP page and data endpoint (Task3)
    @http.route(
        "/shop/rop/realtime",
        type="http",
        auth="user",
        website=True,
        methods=["GET"],
    )
    def realtime_rop_page(self, **kwargs):
        self._check_rop_access()
        return request.render("technical_test.website_rop_realtime")

    @http.route(
        "/shop/rop/realtime/data",
        type="json",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def realtime_rop_data(self, **kwargs):
        self._check_rop_access()

        products = request.env["product.product"].search([
            ("sale_ok", "=", True),
            ("type", "=", "product"),
            ("qty_available", ">", 5),
        ])
        return [{
            "id": product.id,
            "name": product.display_name,
            "quantity": product.qty_available,
            "status": "In Stock",
            "image_url": f"/web/image/product.product/{product.id}/image_256",
        } for product in products]



