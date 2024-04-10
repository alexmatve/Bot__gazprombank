import json


# class Course:
#     id = 0
#     courses = []
#     names = list()
#
#     def __init__(self, course_name, duration, description, skills, moduls, listeners=None):
#         self.course_name = course_name
#         self.duration = duration
#         self.description = description
#         self.skills = skills
#         self.moduls = moduls
#         self.listeners = listeners
#         self.id = Course.id
#         Course.id += 1
#         Course.courses.append(self)
#
#     @classmethod
#     def set_names(cls):
#         for obj in cls.courses:
#             cls.names.append(obj.course_name)

INFORMATION = '||'

with open('course.json', encoding='utf-8') as f:
    templates = json.load(f)

# for c in templates:
#     course = Course(c['Course_name'], c['Duration'], c['Description'],
#                     c['What_you_will_learn'], c['Course_program'], c.get('Listeners', None))
for c in templates:
    for key, value in c.items():
        if type(value) == list:
            value = ",".join(value)
        INFORMATION += f"{key}: {value}*"
    INFORMATION += "||"

# print(INFORMATION)