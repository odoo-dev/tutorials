from odoo import Command
from odoo.tests import tagged
from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged('post_install', '-at_install')
class TestUi(TestPointOfSaleHttpCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_alternative_product = cls.env['product.template'].create({
            'name': 'Desk Right',
            'available_in_pos': True,
            'type': 'consu',
            'is_storable': True,
            'list_price': 52.00,
            'alternative_name': 'Custom desk',
            'pos_description': """a piece of furniture with a flat, table-style work surface, often used
            for writing, reading, or using a computer, and frequently includes drawers or compartments for storage. """,
        })

        cls.test_product = cls.env['product.product'].create({
            'name': 'Conference Chair',
            'available_in_pos': True,
            'type': 'consu',
            'is_storable': True,
            'list_price': 33.00,
            'alternative_name': 'Premium Chair',
            'pos_alternative_product_ids': [
                Command.link(cls.test_alternative_product.id)
            ],
            'pos_description': 'this is the best chair available in the market',
        })

        cls.env['stock.change.product.qty'].create({
            'product_id': cls.test_product.id,
            'product_tmpl_id': cls.test_product.product_tmpl_id.id,
            'new_quantity': 55.00
        }).change_product_qty()

    def test_cashier_can_see_alternative_product_name(self):
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_tour("/pos/ui?config_id=%d" % self.main_pos_config.id, 'PosAlternativeNameTour', login="pos_user")
        self.start_tour("/pos/ui?config_id=%d" % self.main_pos_config.id, 'SearchProductsWithAlternativeName', login="pos_user")
        self.start_tour("/pos/ui?config_id=%d" % self.main_pos_config.id, 'OrderLinesWithAlternativeName', login="pos_user")

    def test_cashier_can_see_product_information(self):
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_tour("/pos/ui?config_id=%d" % self.main_pos_config.id, 'PosProductInformation', login="pos_user")

    def test_product_available_quantity(self):
        self.main_pos_config.with_user(self.pos_user).open_ui()
        self.start_tour("/pos/ui?config_id=%d" % self.main_pos_config.id, 'PosProductAvailableQty', login="pos_user")
        self.env['stock.change.product.qty'].create({
            'product_id': self.test_product.id,
            'product_tmpl_id': self.test_product.product_tmpl_id.id,
            'new_quantity': 80.00
        }).change_product_qty()
        self.start_tour("/pos/ui?config_id=%d" % self.main_pos_config.id, 'PosProductQuantitySyncBtn', login="pos_user")
