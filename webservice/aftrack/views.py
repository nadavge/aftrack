from flask import request, redirect, render_template
from flask.ext.login import login_user, current_user
from aftrack import app, login_manager
from aftrack.models import User
from aftrack.forms import LoginForm

@app.route('/')
def home():
	return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	error = None

	if current_user.is_authenticated:
		return redirect(url_for('home'))

	if request.method == 'POST' and form.validate():
		print('ok')
		user = User.authenticate(form.username.data, form.password.data)
		if user:
			login_user(user, remember=True)
			return redirect(redirect_url())

		error='Wrong username or password.'

	return render_template('login.html', form=form, error=error)


def redirect_url(default='home'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

