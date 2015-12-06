import os
import json
import yaml
import flask
import catalog
import category_forms
import item_forms
import random
import string
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

app = flask.Flask(__name__)

BASEDIR = os.path.split(__name__)[0]


def require_login(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print 'in wrapper'
        from pprint import pprint
        pprint(flask.session)
        if 'username' not in flask.session:
            return flask.redirect('/login')
        else:
            return function(*args, **kwargs)
    return wrapper


@app.route("/")
def root(messages=None):
    categories = catalog.get_all_categories()

    return flask.render_template('home.html', categories=categories,
                                 messages=messages)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    state = ''.join(random.choice(string.ascii_uppercase
                                  + string.digits)
                    for x in range(32))
    flask.session['state'] = state
    return flask.render_template('user_login.html', state=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if flask.request.args.get('state') != flask.session['state']:
        response = flask.make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = flask.request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = flask.make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = flask.make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = flask.make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = flask.make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = flask.session.get('access_token')
    stored_gplus_id = flask.session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = flask.make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    flask.session['access_token'] = credentials.access_token
    flask.session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    flask.session['username'] = data['name']
    flask.session['picture'] = data['picture']
    # flask.session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += flask.session['username']
    output += '!</h1>'
    output += '<img src="'
    output += flask.session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flask.flash("you are now logged in as %s" % flask.session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = flask.session.get('access_token')
    if not access_token:
        return flask.redirect('/')
    print 'In gdisconnect access token is', access_token
    print 'User name is: ', flask.session['username']
    if access_token is None:
        print 'Access Token is None'
        response = flask.make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % flask.session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del flask.session['access_token']
        del flask.session['gplus_id']
        del flask.session['username']
        # del flask.session['email']
        del flask.session['picture']
        response = flask.make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = flask.make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route("/categories/<category_name>")
def category(category_name):
    category_item = catalog.get_category_by_name(category_name)
    items = catalog.get_items_by_category(category_item.id)
    return flask.render_template('category.html',
                                 category=category_item,
                                 items=items)


@app.route("/categories/<category_name>/edit", methods=["GET", "POST"])
@require_login
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
@require_login
def category_add():
    form = category_forms.CategoryAddForm()
    if form.validate_on_submit():
        catalog.create_category(form.name.data, form.description.data)
        return root({'success': "Category added successfully!"})
    print form.errors
    return flask.render_template('category_add.html', form=form)


@app.route("/categories/<category_name>/delete", methods=["GET", "POST"])
@require_login
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
@require_login
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
@require_login
def item_delete(item_id):
    form = item_forms.ItemDeleteForm()
    item_object = catalog.get_item(item_id)
    if form.validate_on_submit():
        catalog.delete_item(item_object.id)
        return root({'success': "Item deleted successfully!"})
    return flask.render_template('item_delete.html', form=form,
                                 item=item_object)


@app.route("/items/add", methods=['GET', 'POST'])
@require_login
def item_add():
    form = item_forms.ItemAddForm()
    form.category.choices = [(x.id, x.name) for x in catalog.get_all_categories()]
    if form.validate_on_submit():
        catalog.create_item(form.name.data, int(form.category.data),
                            form.description.data)
        return root({'success': "Item added successfully!"})
    print form.errors
    return flask.render_template('item_add.html', form=form)


@app.route("/catalog.json")
def json_endpoint():
    return json.dumps(catalog.get_database_as_dict())


@app.route("/catalog.yaml")
def yaml_endpoint():
    return yaml.dump(catalog.get_database_as_dict())


app.secret_key = 'T\xec9*\xb1\x11\xdd@\x94\xd5\xbeqD\xa9\xa4\xb4\xa8\xaf\x02\xe8]\xc6\xc3\xdc'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
