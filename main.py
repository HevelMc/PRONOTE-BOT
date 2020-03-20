# -*- coding: utf-8 -*-
import env_file
import pronotepy
import datetime

client = pronotepy.Client(
    'https://0060013g.index-education.net/pronote/eleve.html?login=true')
if client.login(env_file.get(path='.env')['USERNAME'], env_file.get(path='.env')['PASSWORD']):
    print("Login Successful")

homework_backup = {}

def yes_or_no(boolean: bool):
    if boolean:
        return "Oui"
    else:
        return "Non"


def homeworks():
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
        desc = desc.replace("&#039;", "\'")
        color = homework.background_color
        homeworks_list[desc] = [homework.subject.name, desc,
                                yes_or_no(homework.done), homework.date, color]
    return(homeworks_list)

def profs_absents():
    today = datetime.date.today()
    amonthlater = today + datetime.timedelta(weeks=32)
    lessons = client.lessons(today, amonthlater)
    profs_absents_list = []

    for lesson in lessons:
        if lesson.status:
            teacher = lesson.teacher_name
            timedate = lesson.start
            status = lesson.status
            time = datetime.datetime.strftime(lesson.start, "%d/%m/%Y à %H:%M")
            profs_absents_list.append(
                [lesson.subject.name, teacher, time, timedate, status])
    profs_absents_list.sort(key=lambda colonnes: colonnes[3])
    return(profs_absents_list)

def compare_homeworks(dict1, dict2):
    global homework_backup
    _temp = []
    for index, homework in dict1.items():
        if homework[3] < datetime.date.today():
            _temp.append(index)
    for index in _temp:
        dict1.pop(index)

    _difs = []
    for index, backup_homework in dict1.items():
        if dict1.get(index) != dict2.get(index):
            _difs.append(dict1.get(index))
    homework_backup = dict1
    return _difs
