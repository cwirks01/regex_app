from io import StringIO
import json
import multiprocessing
import os
import random
import csv
import datetime
import time
import PyPDF2
# import en_core_web_sm

import pandas as pd

from pymongo import MongoClient, ReturnDocument
from itertools import zip_longest
from .regex_github_lib import *
from .regex_library_loader import *

ROOT = os.getcwd()

def save_library(repo_lib):
    save_lib(repo_lib=repo_lib)


def read_in_pdf(file_path):
    mypdf = open(r'%s' % file_path, mode='rb')
    pdf_document = PyPDF2.PdfFileReader(mypdf)

    text_out = None
    for i in range(pdf_document.numPages):
        page_to_print = pdf_document.getPage(i)
        text_out = page_to_print.extractText()

    return text_out


def add_values_to_json(json_file, values, header):
    # Clean tuples
    a = []
    for value in values:
        value = "".join(value)
        value.replace(" ", "")
        a.append(value)

    # to remove duplicated
    # from list
    res = []
    for i in a:
        if i not in res:
            res.append(i)

    # Ensure values are not being appended to same name
    try:
        json_file[header].extend(res)
    except Exception as e:
        print("%s not listed in JSON file." % e)
        json_file.update({header: res})

    return json_file


def rm_header_dups_json(json_file):
    for a in json_file.keys():
        idx = 0
        for i in json_file[a]:
            if a == i:
                del json_file[a][idx]
                idx -= 1
            idx += 1
    return json_file


def regex_processor_search(regex_library_processor=None, text_in=None):
    # json_data = load_lib(repoDir=os.path.join(os.getcwd(),"repo"))  # For testing purposes
    # text_in = os.path.join(os.getcwd(),"repo\\test_doc.txt")  # For testing purposes
    # with open(text_in, 'r') as file:
    #     text_in = file.read()

    compiled_json_data = {}
    json_regex_data = regex_library_processor
    for regex_item in json_regex_data[0]:
        for each_item in json_regex_data[0][regex_item]:
            item = re.findall(each_item, text_in)
            # using remove() to
            # perform removal
            while "" in item:
                item.remove("")

            # print(item)

            if not item == []:
                compiled_json_data = add_values_to_json(json_file=compiled_json_data, values=item, header=regex_item)
            compiled_json_data = rm_header_dups_json(compiled_json_data)

    

    return [compiled_json_data]


class regex_user_processor:
    def __init__(self, username=None, password=None, userDir=None, userLib=None, gui=False, downloads=None,
                 uploads=None, repo=None, viz=True, root_dir=os.getcwd(), inBrowser=None, db=None, _db="REGEX_db",
                 previousRun_repo=False):
        self.db = db[_db]
        self.regex_library = db['library']
        self.username = username
        self.password = password
        self.inBrowser = inBrowser
        self.downloads_dir = downloads
        self.uploads_dir = uploads
        self.repo_dir = repo
        self.userDir = userDir
        self.userLib = userLib
        self.gui = gui
        self.viz = viz
        self.text = []
        self.all_text = []
        # self.nlp = en_core_web_sm.load() # close for testing
        self._user_dir_name()
        self.root_dir = root_dir
        self.user_root_dir_path = os.path.join(self.root_dir, 'data', self.userDir)
        self.multiprocessing = multiprocessing

    def _user_dir_name(self):
        if self.username is None:
            self.username = str(random.randint(10, 10 ** 9))
            while self.db.users.find_one({"username": self.username}) is not None:
                self.username = str(random.randint(10, 10 ** 9))
            self.db.users.insert_one({"username": self.username,
                                "createdUser": datetime.datetime.now().timestamp()})

        if self.userDir is None:
            try:
                self.userDir = str(self.db.users.find_one({"username": self.username})[0].get("_id"))
            except Exception as e:
                print("%s \nCreating new user documents." % e)
                self.db.users.insert_one({"username": self.username,
                                "createdUser": datetime.datetime.now().timestamp()})
                self.userDir = str(self.db.users.find_one({"username": self.username}).get("_id"))

        self.username = self.username
        self.userDir = self.userDir

    def create_env_dir(self):
        # Loading main regex library for environment creation
        with open("repo//regex_library.json", 'r') as library_file:
            load_library_file = json.load(library_file)

        self.db.users.find_one_and_update({"username": self.username},
                                                        {"$set":{"main_library": load_library_file}},
                                                        return_document=ReturnDocument.AFTER)
        return

    def to_json(self):
        content=dict(username = self.username,
                    password = self.password,
                    inBrowser = self.inBrowser,
                    downloads_dir = self.downloads_dir,
                    uploads_dir = self.uploads_dir,
                    repo_dir = self.repo_dir,
                    userDir = self.userDir,
                    userLib = self.userLib,
                    gui = self.gui,
                    viz = self.viz,
                    text = self.text,
                    all_text = self.all_text,
                    root_dir = self.root_dir,)
        return content
    
    def load_files(self):
        filePathList = []
        for file in os.listdir(self.uploads_dir):
            fp = os.path.join(self.uploads_dir, file)
            filePathList.append(fp)
        filePathName = filePathList
        return filePathName

    def read_txt(self):
        '''
        User will have their designated library that they can update. repo library will be 
        initially loaded with a main library from source.
        '''
        
        # Loading in a library of previous runs in json
        try:
            self.regex_library = self.db.users.find({'username': self.username})[0]['repository']
            if self.regex_library == {}:
                raise UnboundLocalError('My exit condition was met. Leaving try block')
        except Exception as e:
            print("%s \nCreating Repo" % e)

            json_lib_main = self.db.users.find({'username': self.username})[0]['main_library']['regex']

            self.db.users.find_one_and_update({'username': self.username},
                                        {"$set": {"repository": [
                                            {"filename": "data-repo-%s.json" % time.strftime("%d%m%Y"),
                                            "text": json_lib_main}]}},
                                        return_document=ReturnDocument.AFTER)
            self.regex_library = self.db.users.find({'username': self.username})[0]['repository']

        json_lib = self.regex_library[0]['text']
        # Loading in files from database upload
        for file_input in self.db.users.find({'username': self.username})[0]['uploads']:
            json_lib = regex_processor_search(regex_library_processor=json_lib, text_in=file_input['text'])

            self.all_text.append(file_input['text'])
            print('Finished processing ' + file_input['filename'])

        self.db.users.find_one_and_update({'username': self.username},
                                    {"$set": {"repository": [
                                        {"filename": self.regex_library[0]['filename'],
                                         "text": json_lib}]}},
                                    return_document=ReturnDocument.AFTER)

        self.save_products(json_data=json_lib)

        return

    def create_product(self):
        return

    def save_products(self, json_data=None):

        f = []
        for header in json_data[0]:
            a = [header]
            for item in json_data[0][header]:
                a.append(item)
            f.append(a)

        output_csv = StringIO()
        csvfile = csv.writer(output_csv)
        for item in zip_longest(*f):
            csvfile.writerow(item)
        
        output_csv.seek(0)


        self.db.users.find_one_and_update({"username": self.username},
                                    {"$set": {"downloads": 
                                    [{"data.json": json_data,
                                    "data.csv": output_csv.read()}]}},
                                    return_document=ReturnDocument.AFTER)
        return
    
    def download_file(self, filename, file_in):
        if filename in ["data.csv"]:
            file_in = eval(file_in)
            df_data = pd.DataFrame(pd.json_normalize(file_in).squeeze()).transpose()
        else:
            pass

        if filename == "data.csv":
            file_out = df_data.to_csv(index=False)
        elif filename == "data.json":
            file_out = eval(file_in)

        else:
            file_out = file_in

        return file_out


    def run(self):
        self.read_txt()
