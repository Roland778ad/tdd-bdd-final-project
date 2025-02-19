# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

logger = logging.getLogger("flask.app")

######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    ###################
    # TEST CASES HERE #
    ###################

    # Test READ function of application
    def test_read_product(self):
        """It should read a Product"""
        product = ProductFactory()
        logger.info(f"Building fake product: {product.name}")
        product.id = None
        product.create()
        # Use find() to fetch the product from DB
        found_product = product.find(product.id)
        self.assertEqual(product.id, found_product.id)
        self.assertEqual(product.name, found_product.name)
        self.assertEqual(product.description, found_product.description)
        self.assertEqual(product.price, found_product.price)

    # Test the UPDATE function of application
    def test_update_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        logger.info(f"Building fake product: {product.name}")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        logger.info(f"Created product in DB: {product.name}")
        # Updating product description
        new_description = "This is the new product description"
        product.description = new_description
        # Make sure orig ID is preserved for testing
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, new_description)
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, new_description)

    # Test the DELETE function of application
    def test_delete_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        logger.info(f"Building fake product: {product.name}")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        logger.info(f"Created product in DB: {product.name}")
        # Checking if DB have 1 item
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    # Test the LIST ALL function of application
    def test_list_all_product(self):
        """It should List all Products"""
        self.assertEqual(Product.all(), [])
        logger.info("Building 5 fake products")
        for _ in range(5):
            product = ProductFactory()
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        logger.info("5 products created in DB")
        # Checking if DB have 5 items
        self.assertEqual(len(Product.all()), 5)

    # Test the FIND by NAME function of application
    def test_find_by_name_product(self):
        """It should find a Product by name"""
        logger.info("Building 5 fake products")
        # creating a list of 5 products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        logger.info("5 products created in DB")
        name = products[0].name
        # list comprehension to find list of same names
        count = len([product.name for product in products if name == product.name])
        # count2 = list(Product.find_by_name(prod1_name))
        # self.assertEqual(count, len(count2))
        # Same as above, you can use count() of a query
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    # Test the FIND by AVAILABILITY function of application
    def test_find_by_availability(self):
        """It should find a Product by availability"""
        logger.info("Building 10 fake products")
        # creating a list of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        logger.info("10 products created in DB")
        available = products[0].available
        # list comprehension to find list of same names
        count = len([product for product in products if available == product.available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    # Test the FIND by CATEGORY function of application
    def test_find_by_category(self):
        """It should find a Product by Category"""
        logger.info("Building 10 fake products")
        # creating a list of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        logger.info("10 products created in DB")
        category = products[0].category
        # list comprehension to find list of same names
        count = len([product for product in products if category == product.category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        # Check if each item in the 'found' list matches the given category
        for product in found:
            self.assertEqual(product.category, category)

    # Test the FIND by PRICE function of application
    def test_find_by_price(self):
        """It should find a Product by Price"""
        logger.info("Building 10 fake products")
        # creating a list of 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.id = None
            product.create()
            self.assertIsNotNone(product.id)
        logger.info("10 products created in DB")
        price = products[0].price
        # list comprehension to find list of same names
        count = len([product for product in products if price == product.price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        # Check if each item in the 'found' list matches the given category
        for product in found:
            self.assertEqual(product.price, price)
        found_str = Product.find_by_price(str(price))
        self.assertEqual(found_str.count(), count)
