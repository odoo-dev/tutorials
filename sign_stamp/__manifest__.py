{
    "name": "sign_stamp",
    "depends": ["sign"],
    "data": [
        "views/sign_template.xml",
        "data/sign_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sign_stamp/static/src/backend_components/sign_template/*",
            "sign_stamp/static/src/components/**/*",
            "sign_stamp/static/src/dialogs/**/*",
        ],
        "web.qunit_suite_tests": [
            'sign_stamp/static/tests/dialogs/**/*',
        ],
    },
    "license": "OEEL-1",
}
