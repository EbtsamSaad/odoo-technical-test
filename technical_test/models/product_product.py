from odoo import _, api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_products_below_rop(self, product_ids, pos_config_id, order_uid):
        products = self.browse(product_ids).exists()
        pos_config = self.env["pos.config"].browse(pos_config_id).exists()

        if not pos_config:
            return []

        location = pos_config.picking_type_id.default_location_src_id

        if location:
            products = products.with_context(location=location.id)

        low_stock_products = products.filtered(
            lambda product: product.qty_available <= 5
        )

        if low_stock_products:
            self._notify_warehouse_admins(
                low_stock_products,
                pos_config,
                order_uid,
            )

        return [
            {
                "id": product.id,
                "name": product.display_name,
                "qty_available": product.qty_available,
            }
            for product in low_stock_products
        ]

    def _notify_warehouse_admins(self, products, pos_config, order_uid):
        warehouse_admins = self.env.ref(
            "stock.group_stock_manager"
        ).users

        Activity = self.env["mail.activity"]

        for product in products:
            product_template = product.product_tmpl_id

            for user in warehouse_admins:
                summary = _("Check Product ROP")

                activity_note = _(
                    """
                    <p><strong>Low Stock Alert</strong></p>
                    <p>
                        Product: <strong>%(product)s</strong><br/>
                        POS: %(pos)s<br/>
                        Current Quantity: <strong>%(qty)s</strong><br/>
                        POS Order: %(order_uid)s
                    </p>
                    <p>Please check the product Re-Order Point.</p>
                    """
                ) % {
                                    "product": product.display_name,
                                    "pos": pos_config.name,
                                    "qty": product.qty_available,
                                    "order_uid": order_uid,
                                }

                existing_activity = Activity.search([
                    ("res_model", "=", "product.template"),
                    ("res_id", "=", product_template.id),
                    ("user_id", "=", user.id),
                    ("summary", "=", summary),
                    ("note", "ilike", order_uid),
                ], limit=1)

                if existing_activity:
                    continue

                product_template.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary=summary,
                    note=activity_note,
                )