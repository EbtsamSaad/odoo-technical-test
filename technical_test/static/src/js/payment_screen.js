/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        const partner = order.get_partner();

        if (!partner) {
            await this.popup.add(ErrorPopup, {
                title: "Customer Required",
                body: "Please select a customer before validating the order.",
            });
            return;
        }

        if (!partner.phone) {
            await this.popup.add(ErrorPopup, {
                title: "Customer Phone Required",
                body: "The selected customer must have a phone number.",
            });
            return;
        }

        const phone = partner.phone.trim();

        if (!phone.startsWith("+2")) {
            await this.popup.add(ErrorPopup, {
                title: "Invalid Customer Phone",
                body: "The customer phone number must start with +2.",
            });
            return;
        }

        return super.validateOrder(...arguments);
    },
});