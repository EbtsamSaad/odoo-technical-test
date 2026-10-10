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
        "website_sale",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/rop_product_views.xml",
        "views/pos_config_views.xml",
        "views/website_rop_templates.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "technical_test/static/lib/html2pdf.bundle.min.js",
            "technical_test/static/src/js/product_screen.js",
            "technical_test/static/src/js/payment_screen.js",
            "technical_test/static/src/js/actionpad_widget.js",
            "technical_test/static/src/xml/actionpad_widget.xml",
        ],
    },
    "installable": True,
    "application": False,
}