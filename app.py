from peewee import PostgresqlDatabase, OperationalError, Model, PrimaryKeyField, TextField, IntegerField
from os import path
from time import time
from flask import Flask, Response, render_template, request, jsonify
from flask_cors import CORS
from config import DB_USER, DB_NAME, DB_PASS, DB_HOST, r_ids
from backoff import expo, on_exception
token_secret = "0L3QtSDQu9C10LfRjCDRgdGO0LTQsCwg0YXQsNGG0LrQtdGA"
app = Flask(__name__, static_folder="templates/")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
cors = CORS(app)
app.config.from_object("config")
app.config['CORS_HEADERS'] = 'Content-Type'

URL = 'https://example.ru/'
database = PostgresqlDatabase(
        DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        autorollback=True
    )

@on_exception(expo, OperationalError, max_tries=8)
def create_connection():
    try:
        database.connection()
    except OperationalError:
        database.connect(reuse_if_open=True)


@on_exception(expo, OperationalError, max_tries=8)
def destroy_connection(exc):
    if not database.is_closed():
        database.close()


def init(app):
    app.before_request(create_connection)
    app.teardown_request(destroy_connection)


class BaseModel(Model):
    class Meta:
        database = database

class Premise(BaseModel):
    id = PrimaryKeyField(null=True)
    cadastral_no = TextField()
    region = TextField()
    status = IntegerField()
    r_key = IntegerField()
    date_added = IntegerField()
    date_updated = IntegerField()
    rosreestr_id = TextField()
    url = TextField()
    guid = TextField()
    next = IntegerField()

    class Meta:
        table_name = 'rr'

@app.route("/rosreestr/")
def root():
    return render_template("index.html")

regions = {
    "22": "Алтайский край", 
    "28": "Амурская область", 
    "29": "Архангельская область", 
    "30": "Астраханская область", 
    "31": "Белгородская область", 
    "32": "Брянская область", 
    "33": "Владимирская область", 
    "34": "Волгоградская область", 
    "35": "Вологодская область", 
    "36": "Воронежская область", 
    "79": "Еврейская А.обл.", 
    "75": "Забайкальский край", 
    "37": "Ивановская область", 
    "38": "Иркутская область", 
    "07": "Кабардино-Балкарская Республика", 
    "39": "Калининградская область", 
    "40": "Калужская область", 
    "41": "Камчатский край", 
    "09": "Карачаево-Черкесская Республика", 
    "42": "Кемеровская область", 
    "43": "Кировская область", 
    "44": "Костромская область", 
    "23": "Краснодарский край", 
    "24": "Красноярский край", 
    "45": "Курганская область", 
    "46": "Курская область", 
    "47": "Ленинградская область", 
    "48": "Липецкая область", 
    "49": "Магаданская область", 
    "77": "Москва", 
    "50": "Московская область", 
    "51": "Мурманская область", 
    "83": "Ненецкий АО", 
    "52": "Нижегородская область", 
    "53": "Новгородская область", 
    "54": "Новосибирская область", 
    "55": "Омская область", 
    "56": "Оренбургская область", 
    "57": "Орловская область", 
    "58": "Пензенская область", 
    "59": "Пермский край", 
    "25": "Приморский край", 
    "60": "Псковская область", 
    "01": "Республика Адыгея", 
    "04": "Республика Алтай", 
    "02": "Республика Башкортостан", 
    "03": "Республика Бурятия", 
    "05": "Республика Дагестан", 
    "06": "Республика Ингушетия", 
    "08": "Республика Калмыкия", 
    "10": "Республика Карелия", 
    "11": "Республика Коми", 
    "90": "Республика Крым", 
    "12": "Республика Марий Эл", 
    "13": "Республика Мордовия", 
    "14": "Республика Саха (Якутия)", 
    "15": "Республика Северная Осетия", 
    "16": "Республика Татарстан", 
    "17": "Республика Тыва", 
    "19": "Республика Хакасия", 
    "61": "Ростовская область", 
    "62": "Рязанская область", 
    "63": "Самарская область", 
    "78": "Санкт-Петербург", 
    "64": "Саратовская область", 
    "65": "Сахалинская область", 
    "66": "Свердловская область", 
    "91": "Севастополь", 
    "67": "Смоленская область", 
    "26": "Ставропольский край", 
    "68": "Тамбовская область", 
    "69": "Тверская область", 
    "70": "Томская область", 
    "71": "Тульская область", 
    "72": "Тюменская область", 
    "18": "Удмуртская Республика", 
    "73": "Ульяновская область", 
    "27": "Хабаровский край", 
    "86": "Ханты-Мансийский АО", 
    "74": "Челябинская область", 
    "20": "Чеченская Республика", 
    "21": "Чувашская Республика", 
    "87": "Чукотский АО",
    "89": "Ямало-Ненецкий АО",
    "76": "Ярославская область"
}


@app.route("/rosreestr/sendKadastr", methods=['GET', 'POST'])
def sendKadastr():
    
    token = request.form.get('token')
    if token is None:
        return {'status': "Error", 'code': 1, 'desc': "token param not found"}, 500
    if token != token_secret:
        return {'status': "Error"}, 401
    
    kadastr = request.form.get('kadastr')
    if kadastr is None:
        return {'status': "Error", 'code': 1, 'desc': "kadastr param not found"}, 500
    kadastr = kadastr.replace(' ', '')

    try:
        region = regions[kadastr[:2]]
    except:
        return {'status': "Error", 'code': 1, 'desc': "region param not found"}, 500

    r_key = request.form.get('key')
    if r_key is None:
        return {'status': "Error", 'code': 1, 'desc': "key param not found"}, 500
    try:
        r_key = int(r_key)
    except:
        return {'status': "Error", 'code': 1, 'desc': "key not int"}, 500
    if r_key != 1 and r_key != 2:
        return {'status': "Error", 'code': 1, 'desc': "key not 1 or 2"}, 500
    
    f = open("index.txt", "r")
    try:
        index = int(f.read()) + 1 
    except:
        index = 10

    f.close()
    
    f = open("index.txt", "w")
    f.write(str(index))
    f.close()
    el = Premise(
        cadastral_no=kadastr,
        region=region,
        status=0,
        r_key=r_key,
        date_added=int(time()),
        next=0,
        guid=r_ids[index%len(r_ids)]
    )
    el.save()
    return {'status': "Success", 'number': el.id}, 200

@app.route("/rosreestr/updateGUIDS", methods=['GET', 'POST'])
def updateGUIDS():
    counter = 0
    for el in Premise.select(Premise.id, Premise.guid).where((Premise.status == 0) | (Premise.status == -1)).order_by(Premise.id):
        counter = counter + 1
    max_counter = counter//len(r_ids) + 1 
    index = 1
    r_ids_index = 0
    for el in Premise.select(Premise.id, Premise.guid).where((Premise.status == 0) | (Premise.status == -1)).order_by(Premise.id):
        if index == max_counter:
            index = 1
            r_ids_index = r_ids_index + 1
        index = index + 1
        try:
            query = Premise.update(guid=r_ids[r_ids_index]).where(Premise.id == el.id)
            query.execute() 
        except:
            pass
    return {}

@app.route("/rosreestr/getFileURL", methods=['GET', 'POST'])
def getFileURL():
    try:
        paramID = request.get_json()
    except:
        return {'status': 'error', 'code': 1,  'desc':"ids param not found"}, 500
    
    # if not paramID or 'token' not in paramID:
    #     return {'status': 'error', 'code': 1,  'desc':"token param not found"}, 500

    token = request.args.get('token')
    if token is None:
        return {'status': "Error", 'code': 1, 'desc': "token param not found"}, 500
    if token != token_secret:
        return {'status': "Error"}, 401

    

    if not paramID or 'ids' not in paramID:
        return {'status': 'error', 'code': 1,  'desc':"ids param not found"}, 500
    if paramID['ids'] is None:
        return {'status': 'error', 'code': 1,  'desc':"ids param not found"}, 500
    try:
        ids = [a for a in paramID['ids'] if int(a) > 0]
    except:
        return {'status': 'error', 'code': 1,  'desc':"ids param not found"}, 500

    if len(ids) > 10000:
        return {'status': 'error', 'code': 2,  'desc':"The maximum number of IDs is 1000"}, 500
    answer = []
    for i in ids:
        try:
            el = Premise.select().where(Premise.id == i).get()
        except Premise.DoesNotExist:
            answer.append({"status": 404, 'num':i})
            continue
        if el.status == -1:
            answer.append({"status": 0, "desc":"Waiting api", 'num':el.id})
        if el.status == -2:
            answer.append({"status": 7, "desc":"Not found", 'num':el.id})
        if el.status == -3:
            answer.append({"status": 8, "desc":"Annulirovano", 'num':el.id})

        if el.status == 0:
            answer.append({"status": 0, "desc":"Waiting api", 'num':el.id})
        if el.status == 1:
            answer.append({"status": 1, "desc":"Waiting rr", "time": int((time() - el.date_updated)/60), 'num':el.id, 'index':el.rosreestr_id})
        if el.status == 2:
            answer.append({"status": 2, "desc":"Success", 'url': URL+'rosreestr/download/'+el.url, 'num':el.id, 'index':el.rosreestr_id})
            
        if el.status == 3 or el.status == 4:
            if el.url is not None:
                answer.append({"status": 2, "desc":"Success", 'url': URL+'rosreestr/download/'+el.url, 'num':el.id, 'index':el.rosreestr_id})
            else:
                try:
                    el2 = Premise.select().where(Premise.id == el.next).get()
                except Premise.DoesNotExist:
                    answer.append({"status": 404, 'num':el.id})
                    continue
                if el2.status == 0:
                    answer.append({"status": 3, "desc":"Waiting api 2", 'num':el.id, 'index':el.rosreestr_id})
                if el2.status == 1:
                    answer.append({"status": 4, "desc":"Waiting rr 2", "time1": int((time() - el.date_updated)/60), "time2": int((time() - el2.date_updated)/60), 'num':el.id, 'index':el2.rosreestr_id})
                if el2.status == 2:
                    print("el2.url", el2.url)
                    print("el.id", el.id)
                    print("el2.rosreestr_id", el2.rosreestr_id)
                    answer.append({"status": 5, "desc":"Success 2", 'url': URL+'rosreestr/download/'+el2.url, 'num':el.id, 'index':el.rosreestr_id})
                if el2.status == 4:
                    answer.append({"status": 6, "desc":"Waiting rr full stopped", "time1": int((time() - el.date_updated)/60), "time2": int((time() - el2.date_updated)/60), 'num':el.id, 'index':el.rosreestr_id})
    return jsonify(answer), 200

@app.route("/rosreestr/download/<filename>", methods=['GET', 'POST'])
def download(filename): 
    with open(path.join("runtime/", filename), 'rb') as f:
        data = f.readlines()
    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=%s;' % filename
    }), 200

app.run(host='0.0.0.0', port=5070)
