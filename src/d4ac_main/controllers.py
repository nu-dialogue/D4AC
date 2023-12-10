#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# controllers.py
#
#

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates
import os

f = os.path.abspath(__file__)
dir = os.path.dirname(f)
os.chdir(dir)

app = FastAPI(
    title='dialog application',
    description='dialog application for multi modal',
    version='0.1'
)
app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')
jinja_env = templates.env


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
