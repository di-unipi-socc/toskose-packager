from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required
from flask_babel import _

from api import db
from api.main.models import User
from api.users import bp
from api.users.forms import EditProfileForm


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('username updated'))
        return redirect(url_for('users.edit_profile'))
    elif request.method is 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
