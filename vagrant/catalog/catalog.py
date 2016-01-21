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
    connection = psycopg2.connect(database="item_catalog", user='catalog',
        host='localhost', password='catalog')
    cursor = connection.cursor()
    try:
        yield cursor
    except:
        raise
    else:
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def execute(sql, *args, **kwargs):
    with with_cursor() as cursor:
        return cursor.execute(sql, *args, **kwargs)


def fetch_one(sql, *args, **kwargs):
    with with_cursor() as cursor:
        cursor.execute(sql, *args, **kwargs)
        return cursor.fetchone()


def fetch_all(sql, *args, **kwargs):
    with with_cursor() as cursor:
        cursor.execute(sql, *args, **kwargs)
        return cursor.fetchall()


def clear_database():
    """
    WARNING: This will truncate everything in your database!
    Only use this if you know what you're doing!
    """
    execute("TRUNCATE items;")
    execute("TRUNCATE categories CASCADE;")


def get_database_as_dict():
    """
    Gets the entire database as a data dictionary. Good for
    sending the database as json or yaml.
    """
    data_dict = {'Category': []}
    categories = get_all_categories()
    for category_object in categories:
        items = get_items_by_category(category_object.id)
        category_dict = {
            'id': category_object.id,
            'name': category_object.name,
            'description': category_object.description,
            'Item': [],
        }
        for item_object in items:
            item_dict = {
                'id': item_object.id,
                'name': item_object.name,
                'description': item_object.description,
                'category': item_object.category,
            }
            category_dict['Item'].append(item_dict)
        data_dict['Category'].append(category_dict)
    return data_dict


# ----------------------------------------------------
# ------------- Item Functions -----------------------
# ----------------------------------------------------

def create_item(name, category_id, description=""):
    """
    Creates an item in the database using the given parameters.
    """
    return Item(*fetch_one("INSERT INTO items (name, category, description) " \
                           "VALUES (%s, %s, %s) RETURNING id, name, category, description;",
                           (name, category_id, description)))


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
    item_data = fetch_one("SELECT id, name, category, description "
                          "FROM items WHERE id = %s;", [item_id])
    if not item_data:
        raise NotFoundException("Item not found [{0}]".format(item_id))
    return Item(*item_data)


def update_item(item_id, name, category_id, description):
    """
    Updates the item with id of item_id with given parameters.
    """
    return Item(*fetch_one("UPDATE items SET name = %s, category = %s, description = %s "
                           "WHERE id = %s RETURNING id, name, category, description;",
                           (name, category_id, description, item_id)))


def delete_item(item_id):
    """
    Deletes the item with id of item_id.
    """
    execute("DELETE FROM items WHERE id = %s", (item_id,))


def get_items_by_category(category_id):
    data = fetch_all("SELECT id, name, category, description FROM items "
                     "WHERE category = %s;",
                     (category_id,))
    return map(lambda x: Item(*x), data)


# ----------------------------------------------------
# --------- Category Functions -----------------------
# ----------------------------------------------------

def create_category(name, description=""):
    """
    Creates a category with the given parameters.
    """
    return Category(*fetch_one("INSERT INTO categories (name, description) "
                               "VALUES (%s, %s) RETURNING id, name, description;",
                               (name, description)))


def get_category(category_id):
    """
    Gets the category with the given category_id.
    """
    category_data = fetch_one("SELECT id, name, description "
                              "FROM categories WHERE id = %s;",
                              [category_id])
    if not category_data:
        raise NotFoundException("Category not found [{0}]".format(category_id))
    return Category(*category_data)


def get_category_by_name(name):
    """
    Get the category by the given name.
    """
    category_data = fetch_one("SELECT id, name, description "
                              "FROM categories WHERE name = %s;",
                              [name])
    if not category_data:
        raise NotFoundException("Category not found [{0}].".format(name))
    return Category(*category_data)


def update_category(category_id, name, description):
    """
    Updates the category with the given category_id with given parameters.
    """
    return Category(*fetch_one("UPDATE categories SET name = %s, description = %s "
                               "WHERE id = %s RETURNING id, name, description;",
                               (name, description, category_id)))


def delete_category(category_id):
    """
    Deletes the category with the given category_id.
    """
    execute("DELETE FROM categories WHERE id = %s", (category_id,))


def get_all_categories():
    """
    Returns a list of all of the categories available.
    """
    data = fetch_all("SELECT id, name, description FROM categories;")
    return map(lambda x: Category(*x), data)
