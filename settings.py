from flask import Flask, render_template_string, render_template, request, make_response, send_from_directory, redirect
from datetime import datetime
from lxml import etree
import sqlite3
import random
import os

# ---------------->
app = Flask(__name__)
# ---------------->

