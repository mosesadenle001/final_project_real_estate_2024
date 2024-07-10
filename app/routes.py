from flask import (Blueprint, render_template, url_for, flash, redirect, request,
                   abort)
from __init__ import db, bcrypt
from forms import RegistrationForm, LoginForm, UpdateAccountForm, SubmitListingForm, PropertyForm, ResetPasswordForm, ListingForm, LocationForm
from models import User, Property, Listing, Location
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
from utils import send_reset_email
from utils import save_picture

bp = Blueprint('routes', __name__)

@bp.route("/")
@bp.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    properties = Property.query.order_by(Property.date_posted.desc()).paginate(page=page, per_page=5)
    listings = Listing.query.order_by(Listing.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', properties=properties, listings=listings)


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created successfully')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='R', form=form, button_text="Register")

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('signup.html', title='Login', form=form, button_text="Login")

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('routes.home'))

@bp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated successfully')
        return redirect(url_for('routes.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)
@bp.route("/listing/<int:listing_id>")
def listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('listing.html', title=listing.title, listing=listing)

@bp.route("/property/<int:property_id>")
def property(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('property.html', title=property.title, property=property)

@bp.route("/location/<int:location_id>")
def location(location_id):
    location = Location.query.get_or_404(location_id)
    return render_template('location.html', title=location.name, location=location)


@bp.route("/property/new", methods=['GET', 'POST'])
@login_required
def new_property():
    form = PropertyForm()
    if form.validate_on_submit():
        property = Property(title=form.title.data, description=form.description.data, price=form.price.data, location=form.location.data, owner=current_user)
        db.session.add(property)
        db.session.commit()
        flash('Your property has been created!', 'success')
        return redirect(url_for('routes.home'))
    return render_template('add_listing.html', title='New Property', form=form)

@bp.route("/listing/new", methods=['GET', 'POST'])
@login_required
def new_listing():
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(title=form.title.data, location=form.location.data, content=form.content.data, author=current_user)
        db.session.add(listing)
        db.session.commit()
        flash('Your listing has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_listing.html', title='New Listing', form=form, legend='New Listing')

@bp.route("/location/new", methods=['GET', 'POST'])
@login_required
def new_location():
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(name=form.name.data, description=form.description.data)
        db.session.add(location)
        db.session.commit()
        flash('Your location has been added!', 'success')
        return redirect(url_for('main.home'))
    return render_template('add_location.html', title='New Location', form=form)

@bp.route("/search_by_location")
def search_by_location():
    locations = Location.query.all()
    return render_template('search_by_location.html', title='Search by Location', locations=locations)

@bp.route("/property/<int:property_id>/update", methods=['GET', 'POST'])
@login_required
def update_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner != current_user:
        abort(403)   #handle HTTP exceptions.
    form = PropertyForm()
    if form.validate_on_submit():
        property.title = form.title.data
        property.description = form.description.data
        property.price = form.price.data
        property.location = form.location.data
        db.session.commit()
        flash('Your property has been updated!', 'success')
        return redirect(url_for('routes.property', property_id=property.id))
    elif request.method == 'GET':
        form.title.data = property.title
        form.description.data = property.description
        form.price.data = property.price
        form.location.data = property.location
    return render_template('add_listing.html', title='Update Property', form=form)

@bp.route("/property/<int:property_id>/delete", methods=['POST'])
@login_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner != current_user:
        abort(403)
    db.session.delete(property)
    db.session.commit()
    flash('Your property has been deleted successful')
    return redirect(url_for('routes.home'))

@bp.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        location = request.form.get('location')
        properties = Property.query.filter(Property.location.ilike(f'%{location}%')).all()
        return render_template('location.html', properties=properties, location=location)
    return render_template('search.html')

@bp.route("/compare", methods=['GET', 'POST'])
def compare():
    properties = Property.query.all()
    return render_template('compare.html', properties=properties)

@bp.route("/export_csv")
@login_required
def export_csv():
    properties = Property.query.all()
    data = [{
        'Title': property.title,
        'Description': property.description,
        'Price': property.price,
        'Location': property.location,
        'Date Posted': property.date_posted,
        'Owner': property.owner.username
    }
        for property in properties]
    df = pd.DataFrame(data)
    df.to_csv('properties.csv', index=False)
    flash('Properties have been exported to CSV!', 'success')
    return redirect(url_for('routes.home'))

    mail.send(msg)

def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('routes.login'))
        else:
            flash('No account found with that email.')
    return render_template('reset_password.html', title='Reset Password', form=form)


@bp.route("/submit", methods=['GET', 'POST'])
@login_required
def submit():
    form = SubmitListingForm()
    if form.validate_on_submit():
        listing = Listing(title=form.title.data,
                          location=form.location.data,
                          price=form.price.data,
                          bedrooms=form.bedrooms.data,
                          bathrooms=form.bathrooms.data,
                          description=form.description.data)
        db.session.add(listing)
        db.session.commit()
        flash('Your listing has been submitted!', 'success')
        return redirect(url_for('main.home'))
    return render_template('submit.html', title='Submit Listing', form=form)