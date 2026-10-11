/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

patch(ActionpadWidget.prototype, {
    setup() {
        super.setup(...arguments);
        this.renderer = useService("renderer");
        this.report = useService("report");
    },

    async downloadCashNowReceipt(order) {
        const receiptElement = await this.renderer.toHtml(
            OrderReceipt,
            {
                data: {
                    ...order.export_for_printing(),
                    isBill: false,
                },
                formatCurrency: this.env.utils.formatCurrency,
            }
        );

        const options = {
            margin: 5,
            filename: `POS_Receipt_${order.uid}.pdf`,
            image: {
                type: "jpeg",
                quality: 0.98,
            },
            html2canvas: {
                scale: 2,
                useCORS: true,
            },
            jsPDF: {
                unit: "mm",
                format: [80, 200],
                orientation: "portrait",
            },
        };

        await window.html2pdf()
            .set(options)
            .from(receiptElement)
            .save();
    },

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

        // Cash Now - Direct order processing
        if (!order.is_paid()) {
            await this.popup.add(ErrorPopup, {
                title: "Payment Error",
                body: "The order is not fully paid.",
            });
            return;
        }
        const autoInvoice = this.pos.config.auto_invoice_cash_now;
        console.log(
            "Auto Invoice:",
            this.pos.config.auto_invoice_cash_now
        );

        order.set_to_invoice(autoInvoice);

        order.date_order = luxon.DateTime.now();
        order.finalized = true;
        this.env.services.ui.block();
        let syncResult;
        try {
            // Save POS order directly to backend.
            syncResult = await this.pos.push_single_order(order);
            if (!syncResult || !syncResult.length) {
                order.finalized = false;
                return;
            }
        } catch (error) {
            order.finalized = false;
            throw error;
        } finally {
            this.env.services.ui.unblock();
        }

        // Only proceed after successful backend synchronization.
        if (syncResult?.length) {
            try {
                if (autoInvoice) {
                    await this.downloadCashNowReceipt(order);
                    const accountMoveId = syncResult[0]?.account_move;

                    if (accountMoveId) {
                        await this.report.doAction(
                            "account.account_invoices",
                            [accountMoveId]
                        );
                    } else {
                        console.error(
                            "Cash Now: Order synced, but no invoice was returned."
                        );
                    }
                } else {
                    await this.downloadCashNowReceipt(order);
                }
            } catch (error) {
                console.error("Cash Now PDF download failed:", error);
            }
            this.pos.removeOrder(order);
            this.pos.add_new_order();
            this.pos.showScreen("ProductScreen");
        }


    },
});