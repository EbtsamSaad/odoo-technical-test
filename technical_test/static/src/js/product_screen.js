/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(Order.prototype, {
    async pay() {
        debugger;
        const productIds = [
            ...new Set(
                this.get_orderlines()
                    .map((line) => line.get_product()?.id)
                    .filter(Boolean)
            ),
        ];

        if (!productIds.length) {
            return super.pay(...arguments);
        }
        const lowStockProducts = await this.env.services.orm.call(
            "product.product",
            "get_products_below_rop",
            [
                productIds,
                this.env.services.pos.config.id,
            ]
        );

        if (lowStockProducts.length) {
            const productNames = lowStockProducts
                .map(
                    (product) =>
                        `${product.name} (Available Qty: ${product.qty_available})`
                )
                .join("\n");

            await this.env.services.popup.add(ErrorPopup, {
                title: "Re-Order Point",
                body:
                    "This product is under the Re-Order Point measure\n\n" +
                    productNames,
            });

            return;
        }

        return super.pay(...arguments);
    },
});