import os
from dotenv import load_dotenv
from functools import wraps

import psycopg2
from psycopg2.extras import DictCursor


load_dotenv()
database_url = os.getenv('DATABASE_URL')


def use_cursor(commit=False, cursor_factory=None):

    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            with psycopg2.connect(database_url) as connection:
                with connection.cursor(
                    cursor_factory=cursor_factory
                ) as cursor:
                    result = function(*args, cursor=cursor, **kwargs)
                    if commit:
                        connection.commit()
                    return result
        return inner
    return wrapper


@use_cursor(commit=True, cursor_factory=DictCursor)
def add_url(url, cursor) -> int:
    query = 'INSERT INTO urls (name) VALUES (%s) RETURNING id;'
    cursor.execute(query, (url,))
    return cursor.fetchone()['id']


@use_cursor(cursor_factory=DictCursor)
def get_url_id(url, cursor):
    query = 'SELECT id FROM urls WHERE name = %s;'
    cursor.execute(query, (url,))
    return cursor.fetchone()['id']


@use_cursor(cursor_factory=DictCursor)
def get_urls_with_checks(cursor):
    query = """SELECT
            DISTINCT ON (urls.id)
                urls.id,
                urls.name AS url,
                url_checks.created_at AS last_check,
                url_checks.status_code
            FROM urls LEFT JOIN url_checks
            ON urls.id = url_checks.url_id
            ORDER BY urls.id DESC, url_checks.url_id DESC;"""
    cursor.execute(query)
    return cursor.fetchall()


@use_cursor(cursor_factory=DictCursor)
def get_url_by_id(id, cursor):
    query = 'SELECT * FROM urls WHERE id=%s;'
    cursor.execute(query, (id,))
    return cursor.fetchone()


@use_cursor(cursor_factory=DictCursor)
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


@use_cursor(commit=True)
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
