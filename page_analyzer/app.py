import os
from dotenv import load_dotenv
import requests


from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    abort
)

from page_analyzer.database import (
    add_url as add_url_to_db,
    get_urls_with_checks,
    get_url_by_id,
    get_checks,
    add_check,
    get_url_id
)
from page_analyzer.url import normalize_url, is_url_correct, parse_url


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def main_page():
    return render_template(
        'index.html',
        input_url=''
    )


@app.route('/urls', methods=['POST'])
def add_url():
    url = normalize_url(request.form.get('url'))
    if is_url_correct(url):
        try:
            id = get_url_id(url)
            flash('Страница уже существует', 'info')
        except Exception:
            id = add_url_to_db(url)
            flash('Страница успешно добавлена', 'success')
        return redirect(url_for('url_page', id=id))
    else:
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            input_url=url
        ), 422


@app.route('/urls')
def urls_list():
    return render_template(
        'urls.html',
        urls=get_urls_with_checks()
    )


@app.route('/urls/<id>')
def url_page(id):
    response = get_url_by_id(id)
    if not response:
        abort(404)

    return render_template(
        'url.html',
        id=response['id'],
        url=response['name'],
        created_at=response['created_at'],
        checks=get_checks(id)
    )


@app.route('/urls/<id>/checks', methods=['POST'])
def conduct_check(id):
    try:
        response = requests.get(get_url_by_id(id)['name'])
        response.raise_for_status()
        parsing_result = parse_url(
            response.text
        )
        add_check(
            id,
            response.status_code,
            parsing_result["title"],
            parsing_result["h1"],
            parsing_result["description"]
        )
        flash('Страница успешно проверена', 'success')
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('url_page', id=id))


@app.errorhandler(404)
def page_404(_):
    return render_template(
        '404.html'
    )
