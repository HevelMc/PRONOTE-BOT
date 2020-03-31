# -*- coding: utf-8 -*-
import env_file
import pronotepy
import datetime
import html
import pickle

client = pronotepy.Client(
    'https://0060013g.index-education.net/pronote/eleve.html?login=true')
if client.login(env_file.get(path='.env')['USERNAME'], env_file.get(path='.env')['PASSWORD']):
    print("Login Successful")

homework_backup = {}
profs_backup = {}
manual_add_list = {}


def save_obj(obj, name):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


def yes_or_no(boolean: bool):
    if boolean:
        return "Oui"
    else:
        return "Non"


def relogin():
    try:
        _test = client.current_period
    except:
        if client.login(env_file.get(path='.env')['USERNAME'], env_file.get(path='.env')['PASSWORD']):
            print("Re-Login Successful")
        else:
            print("Re-Login Error !")
    
    #client.login()
    return
    
def homeworks():
    relogin()
    today = datetime.date.today()
    if today.weekday() > 5:
        lundi = today + datetime.timedelta(days=-today.weekday(), weeks=1)
    else:
        lundi = today - datetime.timedelta(days=today.weekday())
    vendredi = lundi + datetime.timedelta(days=4, weeks=4)
    homeworks = client.homework(lundi, vendredi)
    homeworks_list = {}

    for homework in homeworks:
        desc = homework.description
        desc = html.unescape(desc)
        color = homework.background_color
        files = {}
        for file in homework.files:
            files[file.name] = file.url

        homeworks_list[desc] = [homework.subject.name, desc, yes_or_no(homework.done), homework.date, color, files]
    
    manual_add_list = load_obj("manual_add_list")

    _temp = []
    for _index, output in manual_add_list.items():
        if output[3] - lundi < datetime.timedelta(seconds=0):
            _temp.append(_index)
        else:
            homeworks_list[f"{_index}"] = output

    for _index in _temp:
        manual_add_list.pop(_index)

    return(homeworks_list)

def profs_absents():
    relogin()
    today = datetime.date.today()
    amonthlater = today + datetime.timedelta(weeks=32)
    lessons = client.lessons(today, amonthlater)
    profs_absents_list = {}

    for lesson in lessons:
        if lesson.status:
            teacher = lesson.teacher_name
            timedate = lesson.start
            status = lesson.status
            time = datetime.datetime.strftime(lesson.start, "%d/%m/%Y à %H:%M")
            
            if not profs_absents_list.get(time):
                profs_absents_list[time] = [lesson.subject.name, teacher, time, timedate, status]

    return(profs_absents_list)

def list_matieres():
    relogin()
    today = datetime.date.today()
    aweeklater = today + datetime.timedelta(weeks=1)
    lessons = client.lessons(today, aweeklater)
    matieres_list = {}
    for lesson in lessons:
        if not matieres_list.get(lesson.subject.name):
            matieres_list[lesson.subject.name] = lesson.background_color
    return matieres_list

def compare_homeworks(dict1, dict2):
    global homework_backup
    _temp = []
    for index, homework in dict1.items():
        if homework[3] < datetime.date.today():
            _temp.append(index)
    for index in _temp:
        dict1.pop(index)

    _difs = []
    for index, _ in dict1.items():
        if dict1.get(index) != dict2.get(index):
            _difs.append(dict1.get(index))
    homework_backup = dict1
    return _difs

def compare_profs(dict1, dict2):
    global profs_backup
    _temp = []
    for index, absence in dict1.items():
        if index < datetime.date.today():
            _temp.append(index)
    for index in _temp:
        dict1.pop(index)

    _difs = []
    for index, _ in dict1.items():
        if dict1.get(index) != dict2.get(index):
            _difs.append(dict1.get(index))
    profs_backup = dict1
    return _difs
