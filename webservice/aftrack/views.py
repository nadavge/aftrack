from flask import request, redirect, render_template, url_for, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from aftrack import app, login_manager, db
from aftrack.models import User, After
from aftrack.forms import (LoginForm, AfterForm,
	SignupForm, ProfileEditForm, ChangePasswordForm)
from sqlalchemy import extract
from datetime import datetime, timedelta


@app.errorhandler(401)
def access_denied(error):
	flash("You don't have access permission to this page", 'danger')
	return render_template('error.html'), 401


@app.errorhandler(404)
def access_denied(error):
	flash("Sorry, can't find the page you're looking for :(", 'danger')
	return render_template('error.html'), 404


@app.route('/')
@login_required
def home():
	"""Main page, admins can see who's on after, and afters from last 7 days.
	Regular users can set whether they're on after."""
	# TODO maybe seperate into two functions
	if current_user.admin:
		afters = After.query.filter(
			After.user.has(User.yearbook==current_user.yearbook),
			After.start > datetime.utcnow()-timedelta(days=7)
		).all()
		afters_sorted = sorted(afters,
			key=lambda after: after.start, reverse=True)

		on_after = User.query.filter(
			User.afters.any(After.end==None),
			User.yearbook==current_user.yearbook
		)
		on_after_sorted = sorted(on_after,
			key=lambda user:'%s %s'%(user.first_name, user.last_name))
		return render_template('home_admin.html',
			on_after=on_after_sorted,
			afters=afters_sorted
		)

	after = current_user.get_active_after()
	return render_template('home.html', after=after)


@app.route('/afters')
@login_required
def afters_now():
	"""Show afters from current month"""
	if not current_user.admin:
		abort(401)

	return redirect(url_for('afters',
		year=current_user.local_datetime().year,
		month=current_user.local_datetime().month
	))


@app.route('/afters/<int:year>/<int:month>')
@login_required
def afters(year, month):
	"""Show afters in date range"""
	if not current_user.admin:
		abort(401)
	if not 1 <= month <= 12:
		abort(404)

	# Upper bound exclusive, lower bound inclusive
	upper_bound = datetime(year+1, 1, 1) if month==12 else datetime(year, month+1, 1)
	lower_bound = datetime(year, month, 1)

	afters = After.query.filter(
		After.user.has(User.yearbook==current_user.yearbook),
		After.start < current_user.utc_datetime(upper_bound),
		After.start >= current_user.utc_datetime(lower_bound)
	).all()

	afters_sorted = sorted(afters,
		key=lambda after: after.start, reverse=True)

	return render_template('afters.html',
		afters=afters_sorted,
		year=year,
		month=month
	)


@app.route('/users/')
@login_required
def users():
	"""See the list of users from the yearbook of the admin"""
	if not current_user.admin:
		abort(401)

	user_list = sorted(
		User.query.filter_by(yearbook=current_user.yearbook).all(),
		key=lambda user: "%s %s"%(user.first_name, user.last_name)
	)
	return render_template('users.html', users=user_list)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	error = None

	if current_user.is_authenticated:
		return redirect(url_for('home'))

	if request.method == 'POST' and form.validate():
		user = User.authenticate(form.username.data, form.password.data)
		if user:
			login_user(user, remember=True)
			flash('Welcome back {}!'.format(user.first_name),'success')
			return redirect(redirect_url())

		error='Wrong username or password.'

	return render_template('login.html', form=form, error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	error = None

	if current_user.is_authenticated:
		return redirect(url_for('home'))
	print(form.username.data)
	if request.method == 'POST' and form.validate():
		user = User(username=form.username.data,
				password=form.password.data,
				first_name=form.first_name.data,
				last_name=form.last_name.data,
				yearbook=form.yearbook.data)
		db.session.add(user)
		db.session.commit()
		flash('Signed-up succesfully, you may now login.', 'success')
		return redirect(url_for('login'))

	return render_template('signup.html', form=form)


@app.route('/settings/profile', methods=['GET', 'POST'])
@app.route('/settings/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile_edit(username=None):
	"""Change user's personal information"""
	if username:
		user = User.get_by_username(username)
		if not user:
			abort(404)
	else:
		user = current_user

	form = ProfileEditForm()
	if request.method=='POST' and form.validate():
		user.first_name = form.first_name.data
		user.last_name = form.last_name.data
		db.session.commit()
		flash('Profile changed successfully!', 'success')
		return redirect(url_for('profile', username=user.username))
	return render_template('profile_edit.html', form=form, user=user)


@app.route('/settings/admin', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm(current_user)
	if request.method=='POST' and form.validate():
		current_user.set_password(form.new_password.data)
		db.session.commit()
		flash('Password changed successfully, login with the new password', 'success')
		logout_user()
		return redirect(url_for('login'))
	return render_template('change_password.html', form=form)


@app.route('/profile')
@app.route('/profile/<username>')
@login_required
def profile(username=None):
	"""Show user's afters of all time"""
	if username is None:
		user = current_user
	else:
		user = User.get_by_username(username)
		if user is None:
			abort(404)
		if user != current_user and not current_user.admin:
			abort(401)

	afters = sorted(user.afters, key=lambda after:after.start, reverse=True)

	return render_template('profile.html', user=user, afters=afters)


@app.route('/after/add', methods=['GET', 'POST'])
@app.route('/after/add/<username>', methods=['GET', 'POST'])
@login_required
def add_after(username=None):
	"""Add a completely new after"""
	if username:
		user = User.get_by_username(username)
	else:
		user = current_user
	if user is None:
		abort(404)
	elif user != current_user and not current_user.admin:
		abort(401)

	form = AfterForm()

	if request.method=='POST':
		if not form.validate():
			flash('Date or time format were awkward.. Try again', 'danger')
		else:
			local_start, local_end = form.parse()
			after = After(user=user)
			after.start = current_user.utc_datetime(local_start)
			after.end = current_user.utc_datetime(local_end)
			db.session.add(after)
			db.session.commit()
			flash('Added successfully!','success')

			return redirect(url_for('profile',
				username=after.user.username if current_user!=user else None
			))

	return render_template('after_edit.html', form=form)


@app.route('/after/edit/<int:after_id>', methods=['GET', 'POST'])
@login_required
def edit_after(after_id):
	"""Edit a specific after"""
	after = After.query.get(after_id)
	if not after:
		abort(404)
	if after.user != current_user and not current_user.admin:
		abort(401)

	form = AfterForm()

	if request.method=='POST':
		if not form.validate():
			flash('Date or time format were awkward.. Try again', 'danger')
		else:
			local_start, local_end = form.parse()
			after.start = current_user.utc_datetime(local_start)
			after.end = current_user.utc_datetime(local_end)
			db.session.commit()
			flash('Saved successfully!', 'success')
			return redirect(url_for('profile',
				username=after.user.username if current_user!=after.user else None
			))

	return render_template('after_edit.html', form=form, after=after)


@app.route('/after/start')
@login_required
def start_after():
	"""Start a new after"""
	if current_user.admin:
		abort(404)
	after = current_user.get_active_after()
	if after:
		flash("Weird... you asked to start an after, but you're already having one!", "danger")
		return redirect(redirect_url())
	after = After(user=current_user)
	after.start_now()
	db.session.add(after)
	db.session.commit()
	return redirect(redirect_url())


@app.route('/after/end')
@login_required
def end_after():
	"""End the currently running after"""
	if current_user.admin:
		abort(404)
	after = current_user.get_active_after()
	if after is None:
		flash('No currently active after (0_o)', 'danger')
	else:
		after.end_now()
		db.session.commit()
	return redirect(redirect_url())


def redirect_url(default='home'):
	"""Calculate the most fitting url to return to"""
	return (request.args.get('next') or
           request.referrer or
           url_for(default))

