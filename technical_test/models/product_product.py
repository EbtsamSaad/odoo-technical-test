from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def get_products_below_rop(self, product_ids, pos_config_id):
        products = self.browse(product_ids).exists()
        pos_config = self.env["pos.config"].browse(pos_config_id).exists()
        if not pos_config:
            return []
        location = pos_config.picking_type_id.default_location_src_id

        if location:
            products = products.with_context(location=location.id)

        return [
            {
                "id": product.id,
                "name": product.display_name,
                "qty_available": product.qty_available,
            }
            for product in products
            if product.qty_available <= 5
        ]