/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(ActionpadWidget.prototype, {
    async onCashNow() {
        const order = this.pos.get_order();

        if (!order || !order.get_orderlines().length) {
            await this.popup.add(ErrorPopup, {
                title: "Empty Order",
                body: "Please add at least one product before using Cash Now.",
            });
            return;
        }

        // Default customer = admin partner
        const adminPartnerId = await this.env.services.orm.call(
            "res.partner",
            "get_admin_partner_id",
            []
        );

        const adminPartner = this.pos.partners.find(
            (partner) => partner.id === adminPartnerId
        );

        if (!adminPartner) {
            await this.popup.add(ErrorPopup, {
                title: "Admin Customer Not Found",
                body: "The Administrator customer could not be found in the POS.",
            });
            return;
        }
        order.set_partner(adminPartner);

        // Find the cash payment method configured on this POS.
        const cashPaymentMethod = this.pos.payment_methods.find(
            (method) => method.is_cash_count
        );

        if (!cashPaymentMethod) {
            await this.popup.add(ErrorPopup, {
                title: "Cash Payment Method Not Found",
                body: "Please configure a cash payment method for this POS.",
            });
            return;
        }

        // Continue to Cash Now payment...
        const amountDue = order.get_due();
        order.add_paymentline(cashPaymentMethod);

        const paymentLine = order.selected_paymentline;

        if (!paymentLine) {
            await this.popup.add(ErrorPopup, {
                title: "Payment Error",
                body: "Unable to create the cash payment line.",
            });
            return;
        }

        paymentLine.set_amount(amountDue);
        // order.set_to_invoice(true);
        order.cash_now = true;
        this.pos.showScreen("PaymentScreen");

    },
});