import os
import json
import yaml
import flask
import catalog
import category_forms
import item_forms
import flask_login
import flask_openid
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests


CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

app = flask.Flask(__name__)

BASEDIR = os.path.split(__name__)[0]

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
oid = flask_openid.OpenID(app, os.path.join(BASEDIR, 'temp'))


@login_manager.user_loader
def load_user(user_id):
    return catalog.get_user(user_id)


@app.before_request
def lookup_current_user():
    flask.g.user = None
    if 'openid' in flask.session:
        openid = flask.session['openid']
        flask.g.user = catalog.get_user_by_openid(openid=openid)


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


@app.route("/gconnect", methods=['POST'])
def gconnect():
    if flask.request.args.get('state') != flask.session['state']:
        response = flask.make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = flask.request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = flask.make_response(json.dumps('Failed to upgrade the'
                                                  ' authorization code.'),
                                       401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo'
           '?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = flask.make_response(json.dumps(
            result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = flask.make_response(json.dumps(
            "Token's user ID doesn't match given user ID."),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = flask.session.get('credentials')
    stored_gplus_id = flask.session.get('gplus_id')
    if stored_credentials is not None and \
        gplus_id == stored_gplus_id:
        response = flask.make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    flask.session['credentials'] = credentials.access_token
    flask.session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token,
              'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    flask.session['username'] = data['name']
    flask.session['picture'] = data['picture']
    # flask.session['email'] = data['email']

    output = "<h1>Welcome, {session['username']}!</h1>" \
             "<img src=\"{session['picture']\">"
    flask.flash("you are now logged in as {}".format(flask.session['username']))
    return output


@oid.after_login
def create_or_login(resp):
    flask.session['openid'] = resp.identity_url
    user = catalog.get_user_by_openid(openid=resp.identity_url)
    if user is not None:
        flask.flash(u'Successfully signed in')
        flask.g.user = user
        return flask.redirect(oid.get_next_url())
    return flask.redirect(flask.url_for('create_profile', next=oid.get_next_url(),
                          name=resp.fullname or resp.nickname,
                          email=resp.email))


@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if flask.g.user is not None or 'openid' not in flask.session:
        return flask.redirect(flask.url_for('index'))
    if flask.request.method == 'POST':
        name = flask.request.form['name']
        email = flask.request.form['email']
        if not name:
            flask.flash(u'Error: you have to provide a name')
        elif '@' not in email:
            flask.flash(u'Error: you have to enter a valid email address')
        else:
            flask.flash(u'Profile successfully created')
            catalog.create_user(name, email, flask.session['openid'])
            return flask.redirect(oid.get_next_url())
    return flask.render_template('create_profile.html', next=oid.get_next_url())


@app.route('/logout')
def logout():
    flask.session.pop('openid', None)
    flask.flash(u'You were signed out')
    return flask.redirect(oid.get_next_url())


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


@app.route("/catalog.json")
def json_endpoint():
    return json.dumps(catalog.get_database_as_dict())


@app.route("/catalog.yaml")
def yaml_endpoint():
    return yaml.dump(catalog.get_database_as_dict())


app.secret_key = 'T\xec9*\xb1\x11\xdd@\x94\xd5\xbeqD\xa9\xa4\xb4\xa8\xaf\x02\xe8]\xc6\xc3\xdc'

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
