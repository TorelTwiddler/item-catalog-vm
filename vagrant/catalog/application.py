import flask
import catalog
import category_forms
import item_forms

app = flask.Flask(__name__)

@app.route("/")
def root(messages=None):
    categories = catalog.get_all_categories()

    return flask.render_template('home.html', categories=categories,
                                 messages=messages)


@app.route("/categories/<category_name>")
def category(category_name):
    category_item = catalog.get_category_by_name(category_name)
    items = catalog.get_items_by_category(category_item.id)
    return flask.render_template('category.html',
                                 category=category_item,
                                 items=items)


@app.route("/categories/<category_name>/edit", methods=["GET", "POST"])
def category_edit(category_name):
    form = category_forms.CategoryEditForm()
    category_object = catalog.get_category_by_name(category_name)
    if form.validate_on_submit():
        catalog.update_category(category_object.id,
                                form.name.data,
                                form.description.data)
        return root({'success': "Category updated successfully!"})
    print form.errors
    form.name.data = category_object.name
    form.description.data = category_object.description
    return flask.render_template('category_edit.html', form=form,
                                 category=category_object)


@app.route("/category_add", methods=["GET", "POST"])
def category_add():
    form = category_forms.CategoryAddForm()
    if form.validate_on_submit():
        catalog.create_category(form.name.data, form.description.data)
        return root({'success': "Category added successfully!"})
    print form.errors
    return flask.render_template('category_add.html', form=form)


@app.route("/categories/<category_name>/delete", methods=["GET", "POST"])
def category_delete(category_name):
    form = category_forms.CategoryDeleteForm()
    category_object = catalog.get_category_by_name(category_name)
    if form.validate_on_submit():
        catalog.delete_category(category_object.id)
        return root({'success': "Category deleted successfully!"})
    return flask.render_template('category_delete.html', form=form,
                                 category=category_object)


@app.route("/items/<int:item_id>")
def item(item_id):
    item_object = catalog.get_item(item_id)
    return flask.render_template('item.html', item=item_object)


@app.route("/items/<int:item_id>/edit", methods=['GET', 'POST'])
def item_edit(item_id):
    form = item_forms.ItemEditForm()
    form.category.choices = [(x.id, x.name) for x in catalog.get_all_categories()]
    item_object = catalog.get_item(item_id)
    if form.validate_on_submit():
        catalog.update_item(item_object.id,
                            form.name.data,
                            form.category.data,
                            form.description.data)
        return root({'success': "Item updated successfully!"})
    print form.errors
    form.name.data = item_object.name
    form.category.data = item_object.category
    form.description.data = item_object.description
    return flask.render_template('item_edit.html', form=form,
                                 item=item_object)


@app.route("/items/<int:item_id>/delete", methods=['GET', 'POST'])
def item_delete(item_id):
    form = item_forms.ItemDeleteForm()
    item_object = catalog.get_item(item_id)
    if form.validate_on_submit():
        catalog.delete_item(item_object.id)
        return root({'success': "Item deleted successfully!"})
    return flask.render_template('item_delete.html', form=form,
                                 item=item_object)


@app.route("/items/add", methods=['GET', 'POST'])
def item_add():
    form = item_forms.ItemAddForm()
    form.category.choices = [(x.id, x.name) for x in catalog.get_all_categories()]
    if form.validate_on_submit():
        catalog.create_item(form.name.data, int(form.category.data),
                            form.description.data)
        return root({'success': "Item added successfully!"})
    print form.errors
    return flask.render_template('item_add.html', form=form)


app.secret_key = 'T\xec9*\xb1\x11\xdd@\x94\xd5\xbeqD\xa9\xa4\xb4\xa8\xaf\x02\xe8]\xc6\xc3\xdc'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
