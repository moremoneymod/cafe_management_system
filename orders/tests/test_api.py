import pytest
from rest_framework import status
from django.urls import reverse
from ..models import Order


# тесты для API

# тест на успешное добавление заказа
@pytest.mark.django_db
def test_create_order(client):
    url = reverse('order-list')
    order_data = {
        'table_number': 1,
        'items': [{'name': 'Pizza', 'price': 300}],
        'status': 'waiting',
        'total_price': 300,
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'table_number' in response.data  # Проверяем, что в ответе есть поле table_number
    assert 'status' in response.data  # Проверяем, что в ответе есть поле status


# тест на добавление заказа с отсутствием обязательного поля (items)
@pytest.mark.django_db
def test_create_order_missing_field_items(client):
    url = reverse('order-list')
    order_data = {
        # items отсутствует
        'table_number': 1,
        'status': 'waiting',
        'total_price': 300,
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400


# тест на добавление заказа с отсутствием обязательного поля (total_price)
@pytest.mark.django_db
def test_create_order_missing_field_total_price(client):
    url = reverse('order-list')
    order_data = {
        'table_number': 1,
        'items': [{'name': 'Pizza', 'price': 300}],
        'status': 'invalid_status',
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400
    assert 'total_price' in response.data  # Проверяем, что ошибка указывает на отсутствие поля total_price


# тест на добавление заказа с некорректным статусом
@pytest.mark.django_db
def test_create_order_invalid_status(client):
    url = reverse('order-list')
    order_data = {
        'table_number': 1,
        'items': [{'name': 'Pizza', 'price': 300}],
        'status': 'invalid_status',  # Некорректный статус
        'total_price': 300,
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400
    assert 'status' in response.data  # Проверяем, что ошибка указывает на некорректный статус


# тест на добавление заказа с блюдом, имеющим цену 0
@pytest.mark.django_db
def test_create_order_zero_price(client):
    url = reverse('order-list')
    order_data = {
        'table_number': 1,
        'items': [{'name': 'Pizza', 'price': 0}],  # Цена блюда равна 0
        'status': 'waiting',
        'total_price': 0,  # Итоговая стоимость так же 0
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400
    assert 'items' in response.data  # Ожидаем ошибку для items (цена не может быть нулевой)


# тест на добавление заказа с блюдом, имеющим отрицательную цену
@pytest.mark.django_db
def test_create_order_negative_price(client):
    url = reverse('order-list')
    order_data = {
        'table_number': 1,
        'items': [{'name': 'Pizza', 'price': -100}],  # Отрицательная цена
        'status': 'waiting',
        'total_price': -100,  # Итоговая стоимость тоже отрицательная
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400
    assert 'items' in response.data  # Проверка ошибки для поля items (цена не может быть отрицательной)


# тест на добавление заказа с блюдом, имеющим пустое название
@pytest.mark.django_db
def test_create_order_empty_dish_name(client):
    url = reverse('order-list')
    order_data = {
        'table_number': 1,
        'items': [{'name': '', 'price': 300}],  # Пустое название блюда
        'status': 'waiting',
        'total_price': 300,
    }
    response = client.post(url, data=order_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400
    assert 'items' in response.data  # Ошибка по полю items (пустое название блюда)


# тест на получение заказов из базы данных
@pytest.mark.django_db
def test_list_orders(client):
    Order.objects.create(
        table_number=1,
        items=[{'name': 'Pizza', 'price': 300}],
        status='waiting',
        total_price=300
    )
    Order.objects.create(
        table_number=2,
        items=[{'name': 'Burger', 'price': 500}],
        status='ready',
        total_price=500
    )
    url = reverse('order-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный запрос
    assert len(response.data) == 2  # Ожидаем 2 заказа


# тест на получение несуществующего заказа
@pytest.mark.django_db
def test_get_non_existent_order(client):
    url = reverse('order-detail', args=[9999])  # ID несуществующего заказа
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Ожидаем ошибку 404


# тест на получение существующего заказа
@pytest.mark.django_db
def test_get_order(client):
    order = Order.objects.create(
        table_number=1,
        items=[{'name': 'Pizza', 'price': 300}],
        status='waiting',
        total_price=300
    )
    url = reverse('order-detail', args=[order.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный запрос
    assert response.data['table_number'] == order.table_number  # Проверяем, что table_number в ответе соответствует


# тест на обновление заказа
@pytest.mark.django_db
def test_update_order(client):
    order = Order.objects.create(
        table_number=1,
        items=[{'name': 'Pizza', 'price': 300}],
        status='waiting',
        total_price=300
    )
    url = reverse('order-detail', args=[order.id])
    updated_data = {'status': 'ready'}
    response = client.patch(url, data=updated_data, content_type='application/json')
    assert response.status_code == status.HTTP_200_OK  # Ожидаем успешный запрос
    assert response.data['status'] == 'ready'  # Проверяем, что статус был обновлен


# тест на обновление заказа с некорректным статусом
@pytest.mark.django_db
def test_update_order_invalid_status(client):
    order = Order.objects.create(
        table_number=1,
        items=[{'name': 'Pizza', 'price': 300}],
        status='waiting',
        total_price=300
    )
    url = reverse('order-detail', args=[order.id])
    updated_data = {'status': ''}  # Пустой статус
    response = client.patch(url, data=updated_data, content_type='application/json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST  # Ожидаем ошибку 400
    assert 'status' in response.data  # Ошибка по полю status


# тест на удаление заказа
@pytest.mark.django_db
def test_delete_order(client):
    order = Order.objects.create(
        table_number=1,
        items=[{'name': 'Pizza', 'price': 300}],
        status='waiting',
        total_price=300
    )
    url = reverse('order-detail', args=[order.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT  # Ожидаем успешный запрос
    with pytest.raises(Order.DoesNotExist):  # Проверяем, что заказ удален из базы
        Order.objects.get(id=order.id)
