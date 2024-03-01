#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "estate_account",
    "version": "1.0",
    "description": "Connection module between real estate and account invoicing",
    "summary": "estate account",
    "installable": True,
    "application": True,
    "license": "OEEL-1",
    "depends": ["account", "estate"],
    "data": ['report/estate_property_report.xml']
}
