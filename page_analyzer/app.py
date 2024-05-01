import os
from dotenv import load_dotenv

from flask import (
    Flask,
    request,
    render_template,
    flash,
    get_flashed_messages,
    redirect,
    url_for,
    abort
)

from page_analyzer import database, url as url_module


load_dotenv()

app = Flask(__name__)
# For some reason it stops working if either of 2 lines below removed.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def main_page():
    return render_template(
        'index.html',
        input_url='',
        flash_messages=get_flashed_messages(with_categories=True)
    )


@app.route('/urls', methods=['POST'])
def add_url():
    url = url_module.normalize_url(request.form.get('url'))
    if url_module.is_url_correct(url):
        if database.is_url_recorded(url):
            flash('Страница уже существует', 'info')
        else:
            database.add_url(url)
            flash('Страница успешно добавлена', 'success')
        id = database.get_url_id(url)
        return redirect(url_for('url_page', id=id))
    else:
        flash('Некорректный URL', 'error')
        return render_template(
            'index.html',
            input_url=url,
            flash_messages=get_flashed_messages(with_categories=True)
        ), 422


@app.route('/urls')
def urls_list():
    return render_template(
        'urls.html',
        flash_messages=get_flashed_messages(with_categories=True),
        urls=database.get_urls_with_checks()
    )


@app.route('/urls/<id>')
def url_page(id):
    response = database.get_url_by_id(id)
    if not response:
        abort(404)
    id, url, created_at = response

    return render_template(
        'url.html',
        flash_messages=get_flashed_messages(with_categories=True),
        id=id,
        url=url,
        created_at=created_at,
        checks=database.get_checks(id)
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def conduct_check(id):
    try:
        parsing_result = url_module.parse_url(
            database.get_url_by_id(id)[1]
        )
        database.add_check(
            id,
            parsing_result["status_code"],
            parsing_result["title"],
            parsing_result["h1"],
            parsing_result["description"]
        )
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
