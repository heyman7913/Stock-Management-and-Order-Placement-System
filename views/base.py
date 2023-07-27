from app.app import app
from flask import Flask, render_template, abort, request
import os
from models.Customer import *
from flask import make_response
from flask import url_for

# =============================================

GET = "GET"
POST = "POST"
