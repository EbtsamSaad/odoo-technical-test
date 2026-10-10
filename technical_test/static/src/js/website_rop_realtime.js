/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.WebsiteROPRealtime = publicWidget.Widget.extend({
    selector: ".o_website_rop_realtime",

    start() {
        this._isActive = true;
        this._isLoading = false;
        this._lastDataJson = "";
        this._loadProducts();
        this._refreshInterval = setInterval(() => {
            this._loadProducts();
        }, 3000);

        return this._super(...arguments);
    },

    willDestroy() {
        this._isActive = false;
        if (this._refreshInterval) {
            clearInterval(this._refreshInterval);
        }
        this._super(...arguments);
    },

    async _loadProducts() {
        if (this._isLoading || !this._isActive) {
            return;
        }
        this._isLoading = true;
        try {
            const products = await jsonrpc("/shop/rop/realtime/data", {});
            if (this._isActive) {
                this._renderProducts(products);
            }
        } catch (error) {
            console.error("Real-time ROP update failed:", error);
        } finally {
            this._isLoading = false;
        }
    },

    _renderProducts(products) {
        const container = this.el.querySelector("#ropRealtimeProducts");
        if (!container) return;

        // Skip DOM re-rendering if data hasn't changed to prevent UI flicker
        const currentJson = JSON.stringify(products);
        if (this._lastDataJson === currentJson) {
            return;
        }
        this._lastDataJson = currentJson;
        if (!products.length) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted">
                    No products with quantity above 5.
                </div>`;
            return;
        }

        const cardsHtml = products.map(product => `
            <div class="col-md-3">
                <div class="card h-100 p-3">
                    <img src="${product.image_url}" 
                         alt="${product.name}" 
                         class="card-img-top" 
                         style="height: 160px; object-fit: contain;" />
                    <h6 class="mt-3">${product.name}</h6>
                    <p class="text-success mb-1">Quantity: ${product.quantity}</p>
                    <span class="badge bg-success">${product.status}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = cardsHtml;
    },
});