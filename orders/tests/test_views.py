import pytest
from django.urls import reverse
from ..models import Order
from ..forms import OrderForm


@pytest.mark.django_db
@pytest.mark.parametrize('table_number, dish_name, dish_price, total_price, status, expected_count, expected_status', [
    (5, 'Паста', 500.0, 500.0, 'waiting', 1, 302),  # Валидный заказ
    (5, '', 500.0, 850.0, 'waiting', 0, 200),  # Пустое название блюда
    (5, 'Пицца', -200.0, 850.0, 'waiting', 0, 200),  # Отрицательная цена
    (0, 'Суши', 300.0, 850.0, 'waiting', 0, 200),  # Некорректный номер стола
    (5, 'Стейк', 200.0, 850.0, 'invalid_status', 0, 200),  # Некорректный статус
])
def test_create_order(client, table_number, dish_name, dish_price, total_price, status, expected_count,
                      expected_status):
    create_url = reverse('create_order')
    data = {
        'table_number': table_number,
        'status': status,
        'dish_name': [dish_name, dish_name],
        'dish_price': dish_price
    }
    form = OrderForm(data)
    assert form.is_valid() == (expected_count == 1), f'Form errors: {form.errors}'
    response = client.post(create_url, data)
    assert response.status_code == expected_status  # Проверяем статус-код
    assert Order.objects.count() == expected_count  # Проверяем, что заказ создан или нет


@pytest.mark.django_db
@pytest.mark.parametrize('table_number, dish_name, dish_price, total_price, status, expected_count, expected_status', [
    (5, ['Паста', 'Бургер'], ['500.0', '500.0'], 1000, 'waiting', 1, 302),  # Валидный заказ
    (5, '', 500.0, 850.0, 'waiting', 0, 200),  # Пустое название блюда
    (5, 'Пицца', -200.0, 850.0, 'waiting', 0, 200),  # Отрицательная цена
    (0, 'Суши', 300.0, 850.0, 'waiting', 0, 200),  # Некорректный номер стола
    (5, 'Стейк', 200.0, 850.0, 'invalid_status', 0, 200),  # Некорректный статус
])
def test_create_order_many_dishes(client, table_number, dish_name, dish_price, total_price, status, expected_count,
                                  expected_status):
    create_url = reverse('create_order')
    data = {
        'table_number': table_number,
        'status': status,
        'dish_name': dish_name,
        'dish_price': dish_price
    }
    form = OrderForm(data)
    assert form.is_valid() == (expected_count == 1), f'Form errors: {form.errors}'
    response = client.post(create_url, data)
    assert response.status_code == expected_status  # Проверяем статус-код
    assert Order.objects.count() == expected_count  # Проверяем, что заказ создан или нет
