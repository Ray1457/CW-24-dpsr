from Tool import app, db, login_manager
from Tool.models import *
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user





if __name__ == '__main__':
    app.run(debug=True)