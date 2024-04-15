import os
import psycopg2
from flask import Flask, render_template, request, flash, get_flashed_messages
from dotenv import load_dotenv
from validators.url import url as validate_url
from validators import ValidationError
from urllib.parse import urlparse
from datetime import datetime


def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url._replace(
        path='', params='', query='', fragment='').geturl()


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
connection = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.secret_key = "secret_key"


@app.route('/')
def main_page():
    return render_template(
        'index.html',
        input_url='',
        flash_messages=get_flashed_messages(with_categories=True)
        )


@app.route('/urls', methods=['POST'])
def add_url():
    url = normalize_url(request.form.get('url'))
    if isinstance(validate_url(url), ValidationError):
        flash('Некорректный URL', 'error')
        return render_template(
            'index.html',
            input_url=url,
            flash_messages=get_flashed_messages(with_categories=True)
            )
    else:
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                           (url, datetime.now()))
            connection.commit()
            cursor.close()
        return 'success'
