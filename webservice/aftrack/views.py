from flask import request, redirect, render_template, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from aftrack import app, login_manager, db
from aftrack.models import User, After
from aftrack.forms import LoginForm, SignupForm


@app.route('/')
@login_required
def home():
	if current_user.admin or True:
		afters = sorted(After.query.all(), key=lambda after: after.date)
		return render_template('home_admin.html', afters=afters)

	after = current_user.get_active_after()
	return render_template('home.html', after=after)

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


def redirect_url(default='home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

