from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from database.models import User
from database.database import db
from services.audit_service import log_event

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    """
    Decorator to restrict route access to specific roles.
    Example: @role_required('LAB')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            if current_user.role not in roles:
                return render_template(
                    'error.html',
                    error_title="Access Denied",
                    error_message=f"Your account role ({current_user.role}) is unauthorized to access this page."
                ), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user.role)
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        log_event(user.id, "USER_LOGIN", details=f"Logged in from IP: {request.remote_addr}")
        
        # Redirect based on user role
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect_by_role(user.role)

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    logout_user()
    log_event(user_id, "USER_LOGOUT")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

def redirect_by_role(role):
    """Redirects authenticated users to their corresponding dashboards."""
    if role == 'LAB':
        return redirect(url_for('lab.dashboard'))
    elif role == 'PATIENT':
        return redirect(url_for('patient.dashboard'))
    elif role == 'HOSPITAL':
        return redirect(url_for('hospital.dashboard'))
    return redirect(url_for('index'))
