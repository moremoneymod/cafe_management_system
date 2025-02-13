import pytest
from ..forms import OrderForm

@pytest.mark.parametrize('table_number, dish_name, dish_price, total_price, status, is_valid', [
    (1, 'Паста', 500, 500.00, 'waiting', True),  # Валидные данные
    (5, 'Бургер', -350.0, -350.0, 'waiting', False),  # Отрицательная цена
    (5, '', 300.0, 300.0, 'waiting', False),  # Пустое название блюда
    (5, 'Пицца', 0.0, 0.0, 'waiting', False),  # Цена равна нулю
    (0, 'Суши', 250.0, 250.0, 'waiting', False),  # Номер стола меньше 1
    (5, 'Стейк', 200.0, 200.0, 'invalid_status', False),  # Неверный статус
])
def test_order_form(table_number, dish_name, dish_price, total_price, status, is_valid):
    form_data = {
        'table_number': table_number,
        'dish_name': [dish_name],  # Передаем как список
        'dish_price': dish_price,  # Передаем как список
        'status': status,
    }
    form = OrderForm(data=form_data)

    assert form.is_valid() == is_valid