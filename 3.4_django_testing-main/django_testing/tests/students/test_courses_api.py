import pytest
import json
from model_bakery import baker
from rest_framework.test import APIClient

from students.models import Student, Course

@pytest.fixture
def student_factory():
    def factory2(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory2
@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def client():
    return APIClient()


#проверка получения первого курса
@pytest.mark.django_db
def test_first_course(client, course_factory, student_factory):
    students = student_factory(_quantity=5, make_m2m=True)
    courses=course_factory(_quantity=3, students=students, make_m2m=True)
    course_id = courses[0].id
    # print(courses)
    # response = client.get('/api/v1/courses/', {'id': course_id})
    response = client.get(F'/api/v1/courses/{course_id}/')
    data=response.json()
    print(data)
    print(data['students'][0])
    assert response.status_code == 200
    # assert data[0]['name']==courses[0].name
    assert data['name'] == courses[0].name
    assert data['students'][0] == students[0].id

#
#проверка получения списка курсов
@pytest.mark.django_db
def test_list_courses(client, course_factory, student_factory):
    #Arrange
    count = Course.objects.count()
    students = student_factory(_quantity=5, make_m2m=True)
    courses=course_factory(_quantity=3, students=students, make_m2m=True)
    response= client.get('/api/v1/courses/')
    data=response.json()
    assert response.status_code == 200
    for i, c in enumerate(data):
        assert c['name']==courses[i].name
    assert Course.objects.count() == count+3
    assert len(data) == len(courses)
# # #
#проверка фильтрации списка курсов по id
@pytest.mark.django_db
def test_filter_id_courses(client, course_factory, student_factory):
    students = student_factory(_quantity=5, make_m2m=True)
    courses = course_factory(_quantity=3, students=students, make_m2m=True)
    response = client.get('/api/v1/courses/')
    course_id = courses[0].id
    response = client.get('/api/v1/courses/', {'id': course_id})
    data = response.json()
    cour1=Course.objects.filter(id=course_id).values()
    assert response.status_code == 200
    assert data[0]['name']==cour1[0]['name']
# #
#проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_filter_name_courses(client, course_factory, student_factory):
    students = student_factory(_quantity=5, make_m2m=True)
    courses=course_factory(_quantity=3, students=students, make_m2m=True)
    response= client.get('/api/v1/courses/')
    course_name=courses[0].name
    response = client.get('/api/v1/courses/', {'name': course_name})
    data = response.json()
    cour1=Course.objects.filter(name=course_name).values()
    assert response.status_code == 200
    assert data[0]['name']==cour1[0]['name']
# #
#ТЕСТ УСПЕШНОГО СОЗДАНИЯ курса
@pytest.mark.django_db
def test_create_course(client):
    with open('data.json', encoding="utf-8") as f:
        data=json.load(f)
    print(data)
    # course1=client.post('/api/v1/courses/', {'name': data['name'], 'students': data['students']}, format='json')
    # course1 = client.post('/api/v1/courses/', {'name': data['name']}, format='json')
    course1 = client.post('/api/v1/courses/', {'name': data['name']}, format='json')
    response2= client.get('/api/v1/courses/')
    d2=response2.json()
    print(d2)
    course_id=d2[0]['id']
    for st in data['students']:
        st1 = client.post(F'/api/v1/courses/{course_id}/', {'students': [{'name': st['name'], 'birth_date': st['birth_date']}] }, format='json')
    response = client.get('/api/v1/courses/')
    data1=response.json()
    print(data1)
    assert response.status_code == 200
    #assert data1[0]['name']==course1[0].name
    assert len(data1) == 1
# #
#тест успешного обновления курса
@pytest.mark.django_db
def test_update_course(client, course_factory, student_factory):
    students = student_factory(_quantity=3, make_m2m=True)
    courses=course_factory(_quantity=3, students=students, make_m2m=True)
    course_id = courses[0].id
    with open('data.json', encoding="utf-8") as f:
        data=json.load(f)
    print(data)
    course1 = client.patch(F'/api/v1/courses/{course_id}/', data={'name': data['name']})
    response = client.get(F'/api/v1/courses/{course_id}/')
    data1 = response.json()
    print(data1)
    assert response.status_code == 200
    assert data1['name'] == data['name']
# # #
#тест успешного удаления курса.
@pytest.mark.django_db
def test_remove_course(client, course_factory, student_factory):
    students = student_factory(_quantity=3, make_m2m=True)
    courses=course_factory(_quantity=3, students=students, make_m2m=True)
    course_id = courses[0].id
    course1 = client.delete(F'/api/v1/courses/{course_id}/')
    response = client.get('/api/v1/courses/')
    data1 = response.json()
    assert response.status_code == 200
    assert len(data1)==len(courses)-1
