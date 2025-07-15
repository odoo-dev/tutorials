# Server Framework 101
./odoo-bin --addons-path=addons,../enterprise/,../tutorials/ -d rd-demo-enterprise -u estate,estate_account

# OWL (Javascript)
./odoo-bin --addons-path=addons,../enterprise/,../tutorials/ -d rd-demo-case-study-javascript      

# Unit Testing
./odoo-bin --addons-path=addons,../enterprise/,../tutorials/ -d rd-demo-enterprise --test-file=/home/odoo/Tech/Odoo/18.0/tutorials/estate/tests/test_estate.py -u estate,estate_account