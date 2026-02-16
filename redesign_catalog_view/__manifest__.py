{
    "name": "Redesign Catalog View",
    "version": "1.0",
    "author": "Radhey Detroja(RADET)",
    "depends": ["purchase", "sale"],
    "data": ["views/redesign_catalog_view.xml"],
    "appication": False,
    "sequence": 1,
    "license": "LGPL-3",
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "redesign_catalog_view/static/src/**/*",
        ],
    },
}
