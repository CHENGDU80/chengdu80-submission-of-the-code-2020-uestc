from flask import Blueprint, request, g, url_for
import db

bp = Blueprint('graph', __name__, url_prefix='/graph')

