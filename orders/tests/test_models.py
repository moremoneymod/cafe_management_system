import pytest
from django.core.exceptions import ValidationError
from ..models import Order

@pytest.mark.django_db
def test_order_creation():
    # Тест на успешное создание заказа
    order = Order.objects.create(
        table_number=5,
        items=[{'name': 'Паста', 'price': 500}],
        status='waiting'
    )
    assert order.table_number == 5
    assert order.status == 'waiting'
    assert order.total_price == 500.0

@pytest.mark.django_db
def test_order_creation_missing_items():
    # Тест на создание заказа без обязательного поля `items`
    with pytest.raises(ValidationError):
        Order.objects.create(
            table_number=5,
            status='waiting'
        )

@pytest.mark.django_db
def test_order_creation_zero_price():
    # Тест на создание заказа с блюдом, имеющим цену 0
    with pytest.raises(ValidationError):
        Order.objects.create(
            table_number=5,
            items=[{'name': 'Паста', 'price': 0}],
            status='waiting'
        )

@pytest.mark.django_db
def test_order_creation_negative_price():
    # Тест на создание заказа с блюдом, имеющим отрицательную цену
    with pytest.raises(ValidationError):
        Order.objects.create(
            table_number=5,
            items=[{'name': 'Паста', 'price': -10.99}],
            status='waiting'
        )

@pytest.mark.django_db
def test_order_creation_empty_dish_name():
    # Тест на создание заказа с блюдом, имеющим пустое название
    with pytest.raises(ValidationError):
        Order.objects.create(
            table_number=5,
            items=[{'name': '', 'price': 10.99}],
            status='waiting'
        )

@pytest.mark.django_db
def test_order_total_price_calculation():
    # Тест на корректное вычисление `total_price` на основе цен блюд
    order = Order.objects.create(
        table_number=5,
        items=[{'name': 'Паста', 'price': 10.99}, {'name': 'Пицца', 'price': 15.99}],
        status='waiting'
    )
    # Ожидаем, что сумма total_price будет 26.98
    assert order.total_price == 26.98

@pytest.mark.django_db
def test_order_creation_with_invalid_status():
    # Тест на создание заказа с неверным статусом
    with pytest.raises(ValidationError):
        Order.objects.create(
            table_number=5,
            items=[{'name': 'Паста', 'price': 10.99}],
            status='invalid_status'
        )
