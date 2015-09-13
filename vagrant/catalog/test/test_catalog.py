"""
unittests for catalog.py.
"""

import unittest
import psycopg2
from catalog import *

class TestConnection(unittest.TestCase):

	def test_with_cursor(self):
		with with_cursor() as cursor:
			self.assertFalse(cursor.closed, "Cursor closed early.")
		self.assertTrue(cursor.closed, "Cursor did not close.")


class TestCategories(unittest.TestCase):

	def test_create_category(self):
		category = create_category("test", "test_description")
		category2 = create_category("test2")

		with self.assertRaises(psycopg2.IntegrityError):
			create_category("test")

		self.assertEqual(category.name, 'test')
		self.assertEqual(category.description, 'test_description')
		self.assertTrue(category.id)

		self.assertEqual(category2.name, 'test2')
		self.assertEqual(category2.description, '')
		self.assertTrue(category2.id)
		self.assertNotEqual(category.id, category2.id)

		delete_category(category.id)
		delete_category(category2.id)

	def test_get_category(self):
		created = create_category("test", "test_description")

		got = get_category(created.id)
		self.assertEqual(created.id, got.id)
		self.assertEqual(created.name, got.name)
		self.assertEqual(created.description, got.description)

		delete_category(created.id)

	def test_get_category_by_name(self):
		created = create_category("test")

		got = get_category_by_name(created.name)
		self.assertEqual(created.id, got.id)
		self.assertEqual(created.name, got.name)
		self.assertEqual(created.description, got.description)

		delete_category(created.id)

	def test_update_category(self):
		category = create_category("test", "test_description")

		updated = update_category(category.id, "test2", category.description)
		self.assertEqual(updated.id, category.id)
		self.assertEqual(updated.name, 'test2')
		self.assertEqual(updated.description, category.description)

		updated2 = update_category(category.id, "test3", "changed description")
		self.assertEqual(updated2.id, category.id)
		self.assertEqual(updated2.name, 'test3')
		self.assertEqual(updated2.description, 'changed description')

		delete_category(category.id)

	def test_delete_category(self):
		category = create_category("test")
		category2 = create_category("test2")

		delete_category(category.id)
		with self.assertRaises(NotFoundException):
			get_category(category.id)

		self.assertTrue(get_category(category2.id))

		delete_category(category2.id)
		with self.assertRaises(NotFoundException):
			get_category(category2.id)


class TestItems(unittest.TestCase):
	def setUp(self):
		self.category = create_category("Test Category")
		self.category2 = create_category("Test Category 2")

	def tearDown(self):
		delete_category(self.category.id)
		delete_category(self.category2.id)

	def test_create_item(self):
		item = create_item("test", self.category.id, "test_description")
		self.assertEqual(item.name, 'test')
		self.assertEqual(item.category, self.category.id)
		self.assertEqual(item.description, 'test_description')
		self.assertTrue(item.id)

		item2 = create_item("test", self.category.id)
		self.assertEqual(item2.name, 'test')
		self.assertEqual(item2.category, self.category.id)
		self.assertEqual(item2.description, '')
		self.assertTrue(item2.id)
		self.assertNotEqual(item.id, item2.id)

		delete_item(item.id)
		delete_item(item2.id)

	def test_get_item(self):
		created = create_item("test_item", self.category.id,
						   "test_description")

		got = get_item(created.id)
		self.assertEqual(created.id, got.id)
		self.assertEqual(created.name, got.name)
		self.assertEqual(created.description, got.description)

		delete_item(created.id)

	def test_update_item(self):
		item = create_item("test", self.category.id, "test_description")

		updated = update_item(item.id, "test2", self.category2.id, item.description)
		self.assertEqual(updated.id, item.id)
		self.assertEqual(updated.name, 'test2')
		self.assertEqual(updated.category, self.category2.id)
		self.assertEqual(updated.description, item.description)

		updated2 = update_item(item.id, "test3", item.category, "changed description")
		self.assertEqual(updated2.id, item.id)
		self.assertEqual(updated2.category, item.category)
		self.assertEqual(updated2.name, 'test3')
		self.assertEqual(updated2.description, 'changed description')

		delete_item(item.id)

	def test_delete_item(self):
		item = create_item("test", self.category.id)
		item2 = create_item("test2", self.category.id)

		delete_item(item.id)
		with self.assertRaises(NotFoundException):
			get_item(item.id)

		self.assertTrue(get_item(item2.id))

		delete_item(item2.id)
		with self.assertRaises(NotFoundException):
			get_item(item2.id)

if __name__ == "__main__":
	unittest.main()
