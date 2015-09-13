from flask import Flask

app = Flask(__name__)

@app.route("/")
def display_root():
	return "Root page!"


@app.route("/categories/<category_name>")
def display_category(category_name):
	return "Category: {0}".format(category_name)


@app.route("/items/<int:item_id>")
def display_item(item_id):
	return "Item ID: {0}".format(item_id)


@app.route("/items/<int:item_id>/edit")
def display_item_edit(item_id):
	return "Editing Item ID: {0}".format(item_id)


@app.route("/items/<int:item_id>/delete")
def display_item_delete(item_id):
	return "Deleting Item ID: {0}".format(item_id)


@app.route("/items/add")
def display_item_add():
	return "Adding Item."


if __name__ == "__main__":
	app.run(host="0.0.0.0")
