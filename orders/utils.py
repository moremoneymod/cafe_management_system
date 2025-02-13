from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import redirect
from .forms import OrderForm, OrderSearchForm
from django.shortcuts import render
from django.db.models import Sum
from django.db.models import QuerySet
from .models import Order


def extract_dishes_from_request(request) -> list:
    """
    Извлекает данные о блюдах из POST-запроса и преобразует их в список словарей.
    :param request: POST-запрос
    :return: Список словарей с названиями и ценами блюд
    """
    dish_names, dish_prices = get_dish_data_from_request(request)
    dish_prices = request.POST.getlist('dish_price')
    return convert_dish_data_to_list_of_dicts(dish_names=dish_names, dish_prices=dish_prices)


def get_dish_data_from_request(request) -> tuple:
    """
    Извлекает данные о блюдах из POST-запроса.
    :param request: POST-запрос
    :return: Кортеж из двух списков: названия блюд и их цены
    """
    dish_names = request.POST.getlist('dish_name')
    dish_prices = request.POST.getlist('dish_price')
    return dish_names, dish_prices


def convert_dish_data_to_list_of_dicts(dish_names, dish_prices) -> list:
    """
    Преобразует списки названий и цен блюд в список словарей.
    :param dish_names: Список названий блюд
    :param dish_prices: Список цен блюд
    :return: Список словарей с названиями и ценами блюд
    :raises ValueError: Если цена отрицательная
    """
    items = []

    for name, price in zip(dish_names, dish_prices):
        if name and price:
            items.append({"name": name, "price": float(price)})
    return items


def create_order_from_form(form, items) -> Order:
    """
    Создает и сохраняет заказ на основе данных формы и списка блюд
    :param form: Форма заказа
    :param items: Список словарей с названиями и ценами блюд
    :return: Объект заказа
    """
    order = create_order_instance(form=form)
    set_order_data(order=order, items=items)
    save_order(order=order)
    return order


def create_order_instance(form) -> Order:
    """
    Создает объект заказа на основе формы.
    :param form: Форма заказа
    :return: Объект заказа
    """
    order = form.save(commit=False)
    return order


def set_order_data(order, items: list) -> None:
    """
    Устанавливает список блюд и общую стоимость для заказа.
    :param order: Объект заказа
    :param items: Список словарей с названиями и ценами блюд
    """
    order.total_price = sum(item['price'] for item in items)
    order.items = items


def save_order(order) -> None:
    """
    Сохраняет заказ в базе данных.
    :param order: Объект заказа
    """
    order.save()


def handle_post_create_order(request: HttpRequest) -> HttpResponseRedirect:
    """
    Обрабатывает POST-запрос для создания заказа.
    :param request: HTTP-запрос с данными формы.
    :return: Перенаправление на список заказов.
    """
    form = OrderForm(request.POST)
    if form.is_valid():
        try:
            items = extract_dishes_from_request(request)
            create_and_save_order(form, items)
            return redirect('list_order')
        except ValueError as e:
            form.add_error('dish_price', str(e))
        except ValidationError as e:
            form.add_error('table_number', e)  # Добавляем ошибку в форму
    return render(request, 'orders/order_form.html', {'form': form})


def create_and_save_order(form: OrderForm, items: list) -> None:
    """
    Создает и сохраняет заказ.
    :param form: форма с данными заказа.
    :param items: список блюд для заказа.
    """
    create_order_from_form(form, items)


def handle_post_edit_order(request: HttpRequest, order: Order) -> redirect:
    """
    Обрабатывает POST-запрос для редактирования заказа.
    :param request: HTTP-запрос с данными формы.
    :param order: заказ для редактирования.
    :return: Перенаправление на список заказов.
    """
    form = OrderForm(request.POST, instance=order)
    if form.is_valid():
        items = extract_dishes_from_request(request)
        create_and_save_order(form, items)
        return redirect('list_order')
    return render(request, 'orders/order_form.html', {'form': form, 'order_id': order.id})

def get_filtered_orders(form: OrderSearchForm) -> QuerySet:
    """
    Фильтрует заказы на основе формы.
    :param form: форма с фильтрами.
    :return: отфильтрованные заказы.
    """
    orders: QuerySet = Order.objects.all()
    if form.is_valid():
        table_number = form.cleaned_data.get('table_number')
        status = form.cleaned_data.get('status')
        if table_number:
            orders = orders.filter(table_number=table_number)
        if status:
            orders = orders.filter(status=status)
    return orders


def calculate_total_revenue() -> float:
    """
    Считает общую выручку за смену.
    :return: Общая выручка.
    """
    revenue: QuerySet = Order.objects.filter(status='paid').aggregate(total_revenue=Sum('total_price'))
    return revenue['total_revenue'] or 0


def delete_order_from_db(order: Order) -> None:
    """
    Удаляет заказ из базы данных.
    :param order: заказ для удаления.
    """
    order.delete()
