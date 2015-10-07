import flask
import catalog
import category_forms

app = flask.Flask(__name__)

@app.route("/")
def root(messages=None):
    categories = catalog.get_all_categories()

    return flask.render_template('home.html', categories=categories,
                                 messages=messages)


@app.route("/categories/<category_name>")
def category(category_name):
    return "Category: {0}".format(category_name)


@app.route("/categories/<category_name>/edit")
def category_edit(category_name):
    return "Editing Category: {0}".format(category_name)


@app.route("/category_add", methods=["GET", "POST"])
def category_add():
    form = category_forms.CategoryAddForm()
    if form.validate_on_submit():
        catalog.create_category(form.name.data, form.description.data)
        return root({'success': "Category added successfully!"})
    print form.errors
    return flask.render_template('category_add.html', form=form)


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


app.secret_key = 'T\xec9*\xb1\x11\xdd@\x94\xd5\xbeqD\xa9\xa4\xb4\xa8\xaf\x02\xe8]\xc6\xc3\xdc'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
