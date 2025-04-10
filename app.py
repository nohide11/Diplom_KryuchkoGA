import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import Flask, render_template, request, flash, g, make_response
from FDataBase import FDataBase


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'qwerty'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

def get_site_name(db, site_id):
    cur = db.cursor()
    cur.execute("SELECT name FROM sites WHERE id = ?", (site_id,))
    row = cur.fetchone()
    return row['name'] if row else "Неизвестный сайт"

@app.route('/fir', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not request.form.get("start_date"):
            flash("Введите дату начала")
        elif not request.form.get("end_date"):
            flash("Введите дату окончания")
        elif not request.form.get("site"):
            flash("Выберите сайт")
    return render_template('fir.html')

@app.route('/sec', methods=["POST"])
def second():
    db = get_db()
    dbase = FDataBase(db)

    site_id = request.form.get("site")
    rows_GA = dbase.getGA(site_id)
    rows_YM = dbase.getYM(site_id)
    rows_ERP = dbase.getERPProducts()

    return render_template("sec.html",
                           rows_GA=rows_GA,
                           rows_YM=rows_YM,
                           rows_ERP=rows_ERP,
                           site_id=site_id)

@app.route('/three', methods=["POST"])
def three():
    db = get_db()
    dbase = FDataBase(db)

    site_id = request.form.get("site_id")
    rows_GA = dbase.getGA(site_id)
    rows_YM = dbase.getYM(site_id)
    rows_ERP = dbase.getERPProducts()

    return render_template("three.html",
                           rows_GA=rows_GA,
                           rows_YM=rows_YM,
                           rows_ERP=rows_ERP,
                           site_id=site_id)

def generate_plot_image(df, kind, group=None, column=None, title=""):
    fig, ax = plt.subplots()
    try:
        if not df.empty:
            if group:
                df.groupby(group)[column].sum().plot(kind=kind, ax=ax)
            else:
                df[column].value_counts().plot(kind=kind, ax=ax)
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center')
    except Exception as e:
        ax.text(0.5, 0.5, f'Ошибка: {e}', ha='center')
    ax.set_title(title)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return img

@app.route('/dashboard', methods=['POST'])
def dashboard():
    db = get_db()
    dbase = FDataBase(db)

    site_id = int(request.form.get("site_id"))
    site_name = get_site_name(db, site_id)

    df_ga = pd.DataFrame([dict(row) for row in dbase.getGA(site_id)])
    df_ym = pd.DataFrame([dict(row) for row in dbase.getYM(site_id)])
    df_erp = pd.DataFrame([dict(row) for row in dbase.getERPProducts()])
    df_buyers = pd.DataFrame([dict(row) for row in dbase.getERPBuyers()])

    all_images = [
        generate_plot_image(df_ga, 'bar', None, 'location', "GA по локациям"),
        generate_plot_image(df_ga, 'bar', None, 'channel', "GA по каналам"),
        generate_plot_image(df_ym, 'bar', None, 'location', "YM по локациям"),
        generate_plot_image(df_ym, 'bar', None, 'channel', "YM по каналам"),
        generate_plot_image(df_erp, 'bar', 'product_id', 'amount_money', "ERP: сумма по продуктам"),
        generate_plot_image(df_erp, 'bar', None, 'category', "ERP: категории товаров"),
        generate_plot_image(df_erp, 'bar', None, 'product_name', "ERP: популярные продукты"),
        generate_plot_image(df_erp, 'bar', 'category', 'amount_money', "ERP: сумма по категориям"),
        generate_plot_image(df_buyers, 'bar', None, 'product_id', "Покупки по продуктам")
    ]

    return render_template("four.html", all_images=all_images, site_id=site_id, site_name=site_name)

@app.route('/summary', methods=["POST"])
def summary_table():
    db = get_db()
    dbase = FDataBase(db)

    # site_id из формы
    site_id = request.form.get('site_id')

    # загрузка таблиц
    df_buyers = pd.DataFrame([dict(row) for row in dbase.getERPBuyers()])
    df_products = pd.DataFrame([dict(row) for row in dbase.getERPProducts()])
    df_ga = pd.DataFrame([dict(row) for row in dbase.getGA()])
    df_ym = pd.DataFrame([dict(row) for row in dbase.getYM()])
    df_sites = pd.DataFrame([dict(row) for row in dbase.getSites()]) if hasattr(dbase, 'getSites') else pd.DataFrame()

    if df_buyers.empty or df_products.empty or not site_id:
        return render_template("five.html", summary=[], site_name="")

    # приведение типов и соединение продуктов с покупателями
    df_buyers = df_buyers.rename(columns={'id': 'buyer_id'})
    df_buyers['product_id'] = df_buyers['product_id'].astype(int)
    df_products['product_id'] = df_products['product_id'].astype(int)
    df = df_buyers.merge(df_products, on='product_id', how='left')

    # фильтрация GA/YM по site_id
    df_ga = df_ga[df_ga['site_id'] == int(site_id)]
    df_ym = df_ym[df_ym['site_id'] == int(site_id)]

    # добавляем поле source
    df_ga['source'] = 'GA'
    df_ym['source'] = 'YM'

    # отбираем нужные поля
    df_ga_part = df_ga[['buyer_id', 'location', 'channel', 'site_path', 'visit_date']]
    df_ym_part = df_ym[['buyer_id', 'location', 'channel', 'site_path', 'visit_date']]

    # объединяем визиты
    visits = pd.concat([df_ga_part, df_ym_part], ignore_index=True)

    # соединяем с покупками, но оставляем только покупателей, у которых есть визиты
    summary = df.merge(visits, on='buyer_id', how='inner')

    # переименования
    summary = summary.rename(columns={
        'buyer_name': 'Покупатель',
        'purchase_date': 'Дата покупки',
        'product_name': 'Продукт',
        'category': 'Категория',
        'amount_money': 'Сумма',
        'location': 'Локация',
        'channel': 'Канал',
        'site_path': 'Путь по сайту',
        'visit_date': 'Дата визита'
    })

    columns = ['Покупатель', 'Дата покупки', 'Продукт', 'Категория', 'Сумма',
               'Локация', 'Канал', 'Путь по сайту', 'Дата визита']
    summary = summary[[col for col in columns if col in summary.columns]]

    # получаем название сайта
    site_name = ""
    if not df_sites.empty:
        row = df_sites[df_sites['id'] == int(site_id)]
        if not row.empty:
            site_name = row.iloc[0]['name']

    return render_template("five.html", summary=summary.to_dict(orient="records"), site_name=site_name)

@app.route('/rfc', methods=["GET"])
def rfc_form():
    db = get_db()
    dbase = FDataBase(db)

    # Получаем все записи из таблицы function
    functions = dbase.getFunctions()

    return render_template("six.html", functions=functions)


@app.route('/submit_rfc', methods=["POST"])
def submit_rfc():
    functions = request.form.getlist("function[]")
    toggles = request.form.getlist("toggle[]")
    lifecycles = request.form.getlist("lifecycle[]")

    print("📥 Получен RFC-запрос:")
    for f, t, l in zip(functions, toggles, lifecycles):
        print(f" - Блок: {f}, Тогл: {t}, ЖЦ: {l}")

    flash("RFC-запрос успешно сформирован!")
    return render_template("six.html", functions=get_db().cursor().execute("SELECT * FROM function").fetchall())

def getFunctions(self):
    try:
        self.__cur.execute("SELECT * FROM function")
        return self.__cur.fetchall()
    except Exception as e:
        print("Ошибка чтения функции:", e)
        return []

@app.route('/rfc/download', methods=["POST"])
def rfc_download():
    functions = request.form.getlist("function[]")
    toggles = request.form.getlist("toggle[]")
    lifecycles = request.form.getlist("lifecycle[]")

    lines = ["RFC-документ: Запрос на изменение веб-ресурса\n"]
    for i, (f, t, l) in enumerate(zip(functions, toggles, lifecycles), 1):
        lines.append(f"{i}. Функция: {f}\n   Тогл: {t}\n   Состояние: {l}\n")

    content = "\n".join(lines)

    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=rfc_report.txt"
    response.mimetype = "text/plain"
    return response



if __name__ == "__main__":
    app.run(debug=True)
