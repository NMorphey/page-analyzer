import os
from dotenv import load_dotenv
from functools import wraps

import psycopg2
import psycopg2.extras


load_dotenv()
CONNTECTION = psycopg2.connect(os.getenv('DATABASE_URL'))


def use_cursor(changing_data=False, cursor_type='common'):
    cursor_params = {
        'cursor_factory': psycopg2.extras.DictCursor
    } if cursor_type == 'dict' else {}

    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            with CONNTECTION.cursor(**cursor_params) as cursor:
                result = function(*args, cursor=cursor, **kwargs)
                if changing_data:
                    CONNTECTION.commit()
                return result
        return inner
    return wrapper


@use_cursor()
def is_url_recorded(url, cursor):
    query = 'SELECT * FROM urls WHERE name=%s;'
    cursor.execute(query, (url,))
    return bool(cursor.fetchall())


@use_cursor(changing_data=True, cursor_type='dict')
def add_url(url, cursor) -> int:
    query = 'INSERT INTO urls (name) VALUES (%s) RETURNING id;'
    cursor.execute(query, (url,))
    return cursor.fetchone()['id']


@use_cursor(cursor_type='dict')
def get_url_id(url, cursor):
    query = 'SELECT id FROM urls WHERE name = %s;'
    cursor.execute(query, (url,))
    return cursor.fetchone()['id']


@use_cursor()
def get_urls_with_checks(cursor):
    query = """SELECT
            DISTINCT ON (urls.id)
                urls.id,
                urls.name,
                url_checks.created_at,
                url_checks.status_code
            FROM urls LEFT JOIN url_checks
            ON urls.id = url_checks.url_id
            ORDER BY urls.id DESC, url_checks.url_id DESC;"""
    cursor.execute(query)
    return cursor.fetchall()


@use_cursor()
def get_url_by_id(id, cursor):
    query = 'SELECT * FROM urls WHERE id=%s;'
    cursor.execute(query, (id,))
    return cursor.fetchone()


@use_cursor()
def get_checks(id, cursor):
    query = """SELECT
                    id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC;"""
    cursor.execute(query, (id,))
    return cursor.fetchall()


@use_cursor(changing_data=True)
def add_check(url_id, status_code, title, h1, description, cursor):
    query = """INSERT INTO
                url_checks (
                url_id, status_code, title, h1, description
                )
                VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(
        query,
        (url_id, status_code, title, h1, description)
    )
