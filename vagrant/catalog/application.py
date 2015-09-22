import flask
import catalog

app = flask.Flask(__name__)

@app.route("/")
def root():
	categories = catalog.get_all_categories()

	return flask.render_template('home.html', categories=categories)


@app.route("/categories/<category_name>")
def category(category_name):
	return "Category: {0}".format(category_name)


@app.route("/categories/<category_name>/edit")
def category_edit(category_name):
	return "Editing Category: {0}".format(category_name)


@app.route("/category_add", methods=["GET", "POST"])
def category_add():
	if flask.request.method == "GET":
		return flask.render_template('category_add.html')
	return flask.render_template('category_add.html')


@app.route("/categories/<category_name>/delete")
def category_delete(category_name):
	return "Deleting Category: {0}".format(category_name)


@app.route("/items/<int:item_id>")
def item(item_id):
	return "Item ID: {0}".format(item_id)


@app.route("/items/<int:item_id>/edit")
def item_edit(item_id):
	return "Editing Item ID: {0}".format(item_id)


@app.route("/items/<int:item_id>/delete")
def item_delete(item_id):
	return "Deleting Item ID: {0}".format(item_id)


@app.route("/items/add")
def item_add():
	return "Adding Item."


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
