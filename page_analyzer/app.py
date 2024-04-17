import os
import psycopg2
from flask import (
    Flask,
    render_template,
    request, flash,
    get_flashed_messages,
    redirect,
    url_for
)
from dotenv import load_dotenv
from validators.url import url as validate_url
from validators import ValidationError
from urllib.parse import urlparse
from datetime import datetime
import requests


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
            cursor.execute('SELECT * FROM urls WHERE name=%s', (url,))
            if cursor.fetchall():
                flash('Страница уже существует', 'info')
            else:
                cursor.execute(
                    'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                    (url, datetime.now()))
                connection.commit()
                flash('Страница успешно добавлена', 'success')
            cursor.execute(
                'SELECT id FROM urls WHERE name = %s',
                (url,)
                )
            id = cursor.fetchone()[0]
        return redirect(url_for('url_page', id=id))


@app.route('/urls')
def urls_list():
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT
                       DISTINCT ON (urls.id)
                           urls.id,
                           urls.name,
                           url_checks.created_at,
                           url_checks.status_code
                       FROM urls LEFT JOIN url_checks
                       ON urls.id = url_checks.url_id
                       ORDER BY urls.id DESC, url_checks.url_id DESC;
                       """)
        return render_template(
            'urls.html',
            flash_messages=get_flashed_messages(with_categories=True),
            urls=cursor.fetchall()
            )


@app.route('/urls/<id>')
def url_page(id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM urls WHERE id=%s', (id,))
        response = cursor.fetchall()[0]
        if not response:
            return render_template(
                '404.html',
                flash_messages=get_flashed_messages(with_categories=True)
            )
        id, url, created_at = response
        cursor.execute("""
                       SELECT
                           id,
                           status_code,
                           h1,
                           title,
                           description,
                           created_at
                       FROM url_checks
                       WHERE url_id = %s
                       ORDER BY id DESC;
                       """, (id,))
        checks = cursor.fetchall()
        return render_template(
            'url.html',
            flash_messages=get_flashed_messages(with_categories=True),
            id=id,
            url=url,
            created_at=created_at,
            checks=checks
        )


@app.route('/urls/<id>/checks', methods=['POST'])
def conduct_check(id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
        try:
            response = requests.get(cursor.fetchall()[0][0])
            response.raise_for_status()
            cursor.execute(
                """
                INSERT INTO
                url_checks (url_id, created_at, status_code)
                VALUES (%s, %s, %s);
                """,
                (id, datetime.now(), response.status_code)
            )
            connection.commit()
            flash('Страница успешно проверена', 'success')
        except Exception:
            flash('Произошла ошибка при проверке', 'error')

    return redirect(url_for('url_page', id=id))


@app.errorhandler(404)
def page_404(_):
    return render_template(
        '404.html',
        flash_messages=get_flashed_messages(with_categories=True)
    )
