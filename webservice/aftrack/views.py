from flask import request, redirect, render_template, url_for, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from aftrack import app, login_manager, db
from aftrack.models import User, After
from aftrack.forms import LoginForm, SignupForm
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
	if current_user.admin:
		afters = After.query.filter(
			After.user.has(User.yearbook==current_user.yearbook),
			After.date > (datetime.now()-timedelta(days=7)).date()
		).all()
		afters_sorted = sorted(afters,
			key=lambda after: after.date, reverse=True)

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
	if not current_user.admin:
		abort(401)

	return redirect(url_for('afters',
		year=datetime.now().year,
		month=datetime.now().month
	))


@app.route('/afters/<int:year>/<int:month>')
@login_required
def afters(year, month):
	if not current_user.admin:
		abort(401)

	afters = After.query.filter(
		After.user.has(User.yearbook==current_user.yearbook),
		extract('year', After.date)==year,
		extract('month', After.date)==month
	).all()

	print(afters)

	afters_sorted = sorted(afters,
		key=lambda after: after.date, reverse=True)

	return render_template('afters.html',
		afters=afters_sorted,
		year=year,
		month=month
	)


@app.route('/users/')
@login_required
def users():
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

@app.route('/profile/edit')
def profile_edit():
	pass

@app.route('/profile')
@app.route('/profile/<username>')
@login_required
def profile(username=None):
	if username is None:
		user = current_user
	else:
		user = User.query.filter_by(username=username).first()
		if user is None:
			abort(404)
		if user != current_user and not current_user.admin:
			abort(401)

	afters = sorted(user.afters, key=lambda after:after.date, reverse=True)

	return render_template('profile.html', user=user, afters=afters)


@app.route('/after/create')
@login_required
def start_after():
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
	after = current_user.get_active_after()
	if after is None:
		flash('No currently active after (0_o)', 'danger')
	else:
		after.end_now()
		db.session.commit()
	return redirect(redirect_url())


def redirect_url(default='home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

