import warnings
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")
warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
warnings.filterwarnings("ignore", message=".*trying to unpickle estimator.*")

from flask import Flask, request, jsonify
from scripts.pygetPlayerInfo import *
from scripts.dbOperations import *
from scripts.pygameAnalyzerAPI import *
from scripts.helperFunctions import *
from scripts.teamRosterInfo import *
from scripts.getRequest import *
from app_init import app

from extensions import db
from models import *


with app.app_context():
    db.create_all()