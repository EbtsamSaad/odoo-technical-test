{
    "name": "Technical Test",
    "version": "17.0.1.0.0",
    "summary": "Technical assessment customizations for Odoo 17",
    "category": "Inventory",
    "author": "Ebtsam Saad",
    "license": "LGPL-3",
    "depends": [
        "product",
        "stock",
        "point_of_sale",
        "mail",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/rop_product_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "technical_test/static/src/js/product_screen.js",
        ],
    },
    "installable": True,
    "application": False,
}