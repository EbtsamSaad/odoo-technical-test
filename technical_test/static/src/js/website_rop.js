
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.WebsiteROP = publicWidget.Widget.extend({
    selector: ".o_website_rop",
    events: {
        "click .js_update_rop_qty": "_onOpenQuantityModal",
        "click .js_close_rop_modal": "_onCloseQuantityModal",
        "click #ropSaveQuantity": "_onSaveQuantity",
    },

    start() {
        this.selectedProductId = null;
        this.modalElement = this.el.querySelector("#ropQuantityModal");
        return this._super(...arguments);
    },

    _onCloseQuantityModal(ev) {
        ev.preventDefault();
        this.modalElement.close();
    },

    _onOpenQuantityModal(ev) {
        ev.preventDefault();
        const button = ev.currentTarget;
        this.selectedProductId = Number(button.dataset.productId);
        this.el.querySelector("#ropProductName").textContent =
            button.dataset.productName;
        this.el.querySelector("#ropNewQuantity").value = "";
        this.el.querySelector("#ropQuantityError").classList.add("d-none");
        this.modalElement.showModal();
    },

    async _onSaveQuantity() {
        const input = this.el.querySelector("#ropNewQuantity");
        const errorElement = this.el.querySelector("#ropQuantityError");
        const saveButton = this.el.querySelector("#ropSaveQuantity");
        const quantity = Number(input.value);
        if (
            input.value.trim() === "" ||
            !Number.isInteger(quantity) ||
            quantity < 0
        ) {
            errorElement.textContent =
                "Please enter a valid non-negative integer quantity.";
            errorElement.classList.remove("d-none");
            return;
        }
        saveButton.disabled = true;
        try {
            const result = await jsonrpc("/shop/rop/update_quantity", {
                product_id: this.selectedProductId,
                quantity,
            });
            if (result.success) {
                this.modalElement.close();
                window.location.reload();
            }
        } catch (error) {
            console.error("ROP quantity update failed:", error);
            errorElement.textContent =
                "Unable to update product quantity. Please check your permissions and try again.";
            errorElement.classList.remove("d-none");
        } finally {
            saveButton.disabled = false;
        }
    },
});
