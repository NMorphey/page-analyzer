import os
from dotenv import load_dotenv
from functools import wraps

import psycopg2


load_dotenv()
CONNTECTION = psycopg2.connect(os.getenv('DATABASE_URL'))


def use_cursor(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        with CONNTECTION.cursor() as cursor:
            result = function(*args, cursor=cursor, **kwargs)
            CONNTECTION.commit()
            return result
    return wrapper


@use_cursor
def is_url_recorded(url, cursor):
    query = 'SELECT * FROM urls WHERE name=%s;'
    cursor.execute(query, (url,))
    return bool(cursor.fetchall())


@use_cursor
def add_url(url, cursor) -> int:
    query = 'INSERT INTO urls (name) VALUES (%s) RETURNING id;'
    cursor.execute(query, (url,))
    return cursor.fetchone()[0]


@use_cursor
def get_url_id(url, cursor):
    query = 'SELECT id FROM urls WHERE name = %s;'
    cursor.execute(query, (url,))
    return cursor.fetchone()[0]


@use_cursor
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


@use_cursor
def get_url_by_id(id, cursor):
    query = 'SELECT * FROM urls WHERE id=%s;'
    cursor.execute(query, (id,))
    return cursor.fetchone()


@use_cursor
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


@use_cursor
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
