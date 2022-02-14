import os
import json

from pymongo import MongoClient, ReturnDocument
from rest_framework.views import APIView
from .Lib.regex_lib_util import regex_user_processor
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response
from flask import Flask, render_template, flash, send_from_directory, make_response, Markup
from django.shortcuts import redirect, render
from django.contrib import messages
# from flask_pymongo import PyMongo
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie


MONGO_DB_USERNAME = os.environ['MONGO_DB_USERNAME']
MONGO_DB_PASSWORD = os.environ['MONGO_DB_PASSWORD']
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = os.environ['MONGO_PORT']

MONGODB_REGEX_URI = 'mongodb://%s:%s@%s:%s/regex_db?authSource=admin'% (MONGO_DB_USERNAME,
                                                                    MONGO_DB_PASSWORD,
                                                                    MONGO_HOST,
                                                                    MONGO_PORT)

MONGODB_USER_URI = 'mongodb://%s:%s@%s:%s/users_db?authSource=admin' % (MONGO_DB_USERNAME,
                                                                        MONGO_DB_PASSWORD,
                                                                        MONGO_HOST,
                                                                        MONGO_PORT)

# app = Flask(__name__)
# app.secret_key = "super secret key"
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# app.config['MONGO_URI'] = MONGODB_REGEX_URI
users_db = MongoClient(MONGODB_USER_URI)
REGEX_db = MongoClient(MONGODB_REGEX_URI)
# mongo = PyMongo(app)

ROOT = os.getcwd()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', "json"}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_view(['GET', 'POST'])
def main(request):
    global main_app
    if request.method == 'POST':
        cookie_name = request.COOKIES.get('_cdub_app_username')
        # cookie_name = request.cookies.get('_cdub_app_username')
        cookie_username = users_db.users_db.user.find_one({"_cookies":cookie_name})
        main_app_user = regex_user_processor(username='cwirks01@gmail.com', db=REGEX_db)
        # main_app_user = regex_user_processor(username=cookie_username['email'], db=REGEX_db)
        # main_app_user.create_env_dir()
        # check if the post request has the file part
        # app.config['RENDER_VIZ'] = bool(request.form.get("renderViz"))

        if (len(request.FILES) == 0) and (request.POST["FreeInputText"] in ['', None]):
            messages.add_message(request, messages.ERROR, 'No files loaded!')
            # flash('No files loaded!')
            return redirect('/regex/')

        if not request.POST["FreeInputText"] in ['', None]:
            text = request.form.getlist("FreeInputText")[0]
            main_app_user.db.find_one_and_update({"username": main_app_user.username},
                                                {"$set": {"uploads": [text]}},
                                                return_document=ReturnDocument.AFTER)
        else:
            files = request.FILES.getlist('inputFileNames')
            for file in files:
                if file and allowed_file(file.name):
                    if file.name.rsplit('.')[-1] == 'json':
                        file_item = secure_filename(file.name)
                        new_file = file.read()
                        text = json.loads(new_file.decode("utf-8"))
                        main_app_user.db.find_one_and_update({"username": main_app_user.username},
                                                        {"$set":{"repository":
                                                        [{"filename": file_item, "text": text}]}},
                                                        return_document=ReturnDocument.AFTER)
                    else:
                        file_item = secure_filename(file.name)
                        new_file = file.read()
                        text = new_file.decode("utf-8")
                        main_app_user.db.users.find_one_and_update({"username": main_app_user.username},
                                                        {"$set": {"uploads":
                                                        [{"filename": file_item, "text": text}]}},
                                                        return_document=ReturnDocument.AFTER)

        messages.add_message(request, messages.INFO, 'File(s) successfully uploaded')
        # flash('File(s) successfully uploaded')
        return redirect('/regex/processing/')

    else:
        try:
            cookie_name = request.COOKIES.get('_cdub_app_username')
            # cookie_username = users_db.users_db.user.find_one({"_cookies":cookie_name})

            # if cookie_username is None:
            #     return redirect("/auth_app", code=302)

            # else:
            # main_app = regex_user_processor(username=cookie_username['email'], db=REGEX_db)
            main_app = regex_user_processor(username='cwirks01@gmail.com', db=REGEX_db)
            context=main_app.to_json()
            return render(request, 'index.html', context)

        except Exception as e:
            print("%s \n moving on" % e)
            pass
            return render(request, 'index.html', context)
            # return redirect("/auth_app", code=302)


def process_files(request):
    global main_app_user
    cookie_name = request.COOKIES.get('_cdub_app_username')
    cookie_username = users_db.users_db.user.find_one({"_cookies":cookie_name})
    main_app_user = regex_user_processor(username='cwirks01@gmail.com', db=REGEX_db)
    # main_app_user = regex_user_processor(username=cookie_username['email'], db=REGEX_db)
    # main_app_user.inBrowser = app.config['RENDER_VIZ']
    main_app_user.run()
    return redirect("/regex/application_ran/")


# @app.route("/regex/application_ran", methods=['GET', 'POST'])
def complete_app(request):
    global main_app_user
    cookie_name = request.COOKIES.get('_cdub_app_username')
    cookie_username = users_db.users_db.user.find_one({"_cookies":cookie_name})
    main_app_user = regex_user_processor(username='cwirks01@gmail.com', db=REGEX_db)
    # main_app_user = regex_user_processor(username=cookie_username['email'], db=REGEX_db)
    # main_app_user.create_env_dir()

    jsonItems = main_app_user.db.users.find({"username": main_app_user.username})[0]["downloads"][0]["data.json"]
    allfiles = main_app_user.db.users.find({"username": main_app_user.username})[0]["downloads"][0]

    all_items = []
    for i in jsonItems[0]:
        all_items.append(list([i, jsonItems[0][i]]))

    user_json = main_app_user.to_json()
    context={
            "all_items":all_items,
            "allfiles":allfiles,
            "main_app":user_json
            }

    return render(request, "app_finish.html", context)


# @app.route('/regex/out/filename/<filename>/file/<file>')
def downloaded_file_db(request, filename, file):
    cookie_name = request.cookies.get('_cdub_app_username')
    main_app_user_db = regex_user_processor(username='cwirks01@gmail.com', db=REGEX_db)
    # main_app_user_db = regex_user_processor(username=cookie_username['email'], db=REGEX_db)

    file_out = main_app_user_db.download_file(filename=filename, file_in=file)
    
    if filename.endswith("json"):
        file_out = json.dumps(file_out)
    else:
        file_out = file_out

    response = Response(file_out, mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename=filename)

    return response
