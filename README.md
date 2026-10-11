# Odoo 17 Technical Assessment

Custom Odoo 17 addon covering **Point of Sale, Inventory, eCommerce, and REST APIs**.

- **Module:** `technical_test`
- **Odoo version:** 17 Enterprise
- **Git branch:** `technical-test`

## Implemented Features

| Area | Features |
| --- | --- |
| **POS** | Stock threshold validation before payment; warehouse notifications for low-stock products; customer phone validation (`+2` prefix); **Cash Now** shortcut. |
| **Inventory** | Outgoing picking date validation; ROP product menus and views; `has_rop` and `rop_count` fields with a related-product smart button. |
| **eCommerce** | Restricted low-stock ROP page; update on-hand quantity with warehouse notifications; realtime ROP view; low-stock JSON endpoint. |
| **REST APIs** | POS orders by date range; products with ROP count; update product ROP count; POS orders by session. |

## Installation

1. Use **Odoo 17 Enterprise** with the required POS, Inventory, and Website/eCommerce applications.
2. Add the `technical_test` directory to your Odoo addons path.
3. Restart Odoo, update the Apps list, and install **Technical Test**.


## Configuration

- Configure POS payment methods, products, and stock locations.
- Assign appropriate POS, Inventory, and Warehouse permissions to users.
- For external API access, generate an **Odoo API key** for a dedicated integration user with the required permissions.
- Send API keys in the `x-api-key` header.

## Key Routes

| Route | Purpose |
| --- | --- |
| `/shop/rop` | ROP view ||
| `/shop/rop/realtime` | Real-time ROP |
| `GET /rop-product` | Products with quantity below 5 |
| `GET /api/orders` | POS orders within a date range |
| `GET /api/products/rop` | Products with ROP count |
| `POST /api/products/rop/update` | Update a product's ROP count |
| `GET /api/pos/sessions/<session_id>/orders` | POS orders for a session |

For authentication, request parameters, and response examples, see **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)**.

## Demo Videos

The following videos demonstrate the key features implemented in the Odoo Technical Assessment.

### **Video 1: Inventory & Point of Sale (POS)**

**[▶ Watch Inventory & POS Demo](https://www.veed.io/view/45abfe79-6252-4b19-8500-fcfee3ac52b5?source=VVP+New+Menu&panel=share)**


### **Video 2: Ecommerce & APIs**

**[▶ Watch Ecommerce & APIs Demo](https://www.veed.io/view/5ef2d89c-349a-466e-8761-553471354e5a?source=editor&panel=share)**

