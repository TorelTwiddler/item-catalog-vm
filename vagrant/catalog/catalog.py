"""
catalog.py is a module used to access the "item_catalog" database.
"""


import psycopg2
import contextlib
from collections import namedtuple

Category = namedtuple("Category", ['id', 'name', 'description'])
Item = namedtuple("Item", ['id', 'name', 'category', 'description'])


class NotFoundException(Exception): pass


@contextlib.contextmanager
def with_cursor():
    """
    Yields a cursor connected to our database. The connection
    will commit after leaving the yield without errors. Both
    the cursor and the connection will always close regardless
    of errors.
    """
    conn = psycopg2.connect("dbname=item_catalog")
    cur = conn.cursor()
    try:
        yield cur
    except:
        raise
    else:
        conn.commit()
    finally:
        cur.close()
        conn.close()


def create_item(name, category_id, description=""):
    """
    Creates an item in the database using the given parameters.
    """
    with with_cursor() as cursor:
        cursor.execute("INSERT INTO items (name, category, description) " \
                       "VALUES (%s, %s, %s) RETURNING id, name, category, description",
                       (name, category_id, description))
        return Item(*cursor.fetchone())


def get_item(item_id):
	"""
	Returns an Item with the given item_id.

	@param item_id: the id of the desired item.
	@type item_id: int
	@return: the Item with the given id.
	@rtype: Item
	@raise: NotFoundException if the given id is not found
		in the database.
	"""
	with with_cursor() as cursor:
		cursor.execute("SELECT id, name, category, description " \
					   "FROM items WHERE id = %s", [item_id])
		item_data = cursor.fetchone()
		if not item_data:
			raise NotFoundException("Item not found [{0}]".format(item_id))
	 	return Item(*item_data)


def update_item(item_id, name, category_id, description):
    """
    Updates the item with id of item_id with given parameters.
    """
    with with_cursor() as cursor:
        cursor.execute("UPDATE items SET name = %s, category = %s, description = %s " \
                       "WHERE id = %s RETURNING id, name, category, description",
                       (name, category_id, description, item_id))
        return Item(*cursor.fetchone())


def delete_item(item_id):
    """
    Deletes the item with id of item_id.
    """
    with with_cursor() as cursor:
        cursor.execute("DELETE FROM items WHERE id = %s",
                       (item_id,))


def create_category(name, description=""):
    """
    Creates a category with the given parameters.
    """
    with with_cursor() as cursor:
        cursor.execute("INSERT INTO categories (name, description) " \
                       "VALUES (%s, %s) RETURNING id, name, description",
                       (name, description))
        return Category(*cursor.fetchone())


def get_category(category_id):
    """
    Gets the category with the given category_id.
    """
    with with_cursor() as cursor:
		cursor.execute("SELECT id, name, description " \
					   "FROM categories WHERE id = %s", [category_id])
		category_data = cursor.fetchone()
		if not category_data:
			raise NotFoundException("Category not found [{0}]".format(category_id))
	 	return Category(*category_data)


def get_category_by_name(name):
    """
    Get the category by the given name.
    """
    with with_cursor() as cursor:
        cursor.execute("SELECT id, name, description " \
                       "FROM categories WHERE name = %s", [name])
        category_data = cursor.fetchone()
        if not category_data:
            raise NotFoundException("Category not found [{0}].".format(name))
        return Category(*category_data)

def update_category(category_id, name, description):
    """
    Updates the category with the given category_id with given parameters.
    """
    with with_cursor() as cursor:
        cursor.execute("UPDATE categories SET name = %s, description = %s " \
                       "WHERE id = %s RETURNING id, name, description",
                       (name, description, category_id))
        return Category(*cursor.fetchone())


def delete_category(category_id):
    """
    Deletes the category with the given category_id.
    """
    with with_cursor() as cursor:
        cursor.execute("DELETE FROM categories WHERE id = %s",
                       (category_id,))
