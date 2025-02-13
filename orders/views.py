from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from .utils import extract_dishes_from_request, delete_order_from_db, handle_post_create_order, create_and_save_order, \
    get_filtered_orders, calculate_total_revenue, handle_post_edit_order
from .forms import OrderForm, OrderSearchForm
from django.shortcuts import render
from django.db.models import Sum
from typing import Union
from django.db.models import QuerySet
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from rest_framework import status
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers


def list_order(request: HttpRequest) -> HttpResponse:
    """
    Отображает на странице список всех заказов с основной информацией.

    Извлекает все заказы из базы данных и передает их в шаблон для отображения.

    :param request: HTTP-запрос, содержащий информацию о текущем запросе пользователя.
    :return: Отображение страницы, содержащей список всех заказов.
    """
    orders: QuerySet = Order.objects.all()
    return render(request, 'orders/order_list.html', {'orders': orders})


def create_order(request: HttpRequest) -> Union[HttpResponseRedirect, HttpResponse]:
    """
    Обрабатывает создание нового заказа.
    :param request: HTTP-запрос, содержащий данные формы для создания заказа.
    :return: Перенаправление на список заказов или отображение формы с ошибками.
    """
    if request.method == 'POST':
        return handle_post_create_order(request)
    else:
        form = OrderForm()
    return render(request, 'orders/order_form.html', {'form': form})


def edit_order(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Отображает форму для редактирования заказа.
    :param request: HTTP-запрос, содержащий данные для редактирования.
    :param pk: ID заказа для редактирования.
    :return: Отображение формы для редактирования заказа.
    """
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        return handle_post_edit_order(request, order)
    else:
        form = OrderForm(instance=order)
    return render(request, 'orders/order_form.html', {'form': form, 'order_id': order.id})


def delete_order(request: HttpRequest, pk: int) -> HttpResponseRedirect:
    """
    Удаляет заказ по ID.
    :param pk: ID заказа для удаления.
    :return: Перенаправление на список заказов.
    """
    order = get_object_or_404(Order, pk=pk)
    delete_order_from_db(order)
    return redirect('list_order')


def search_order(request: HttpRequest) -> HttpResponse:
    """
    Поиск заказов по фильтрам.
    :param request: HTTP-запрос с параметрами поиска.
    :return: Отображение результатов поиска.
    """
    form = OrderSearchForm(request.GET or None)
    orders: QuerySet = get_filtered_orders(form)
    return render(request, 'orders/order_search.html', {'form': form, 'orders': orders})


def calculate_revenue(request: HttpRequest) -> HttpResponse:
    """
    Рассчитывает выручку за смену (заказы со статусом "оплачено").
    :param request: HTTP-запрос.
    :return: Отображение общей выручки.
    """
    total_revenue = calculate_total_revenue()
    return render(request, 'orders/revenue.html', {'total_revenue': total_revenue})


# ViewSet для API
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления заказами.

    Позволяет:
    - Создавать заказы
    - Обновлять заказы
    - Удалять заказы
    - Искать и фильтровать заказы по номеру столика и статусу
    - Получать общую выручку от оплаченных заказов
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['table_number', 'status']
    search_fields = ['table_number', 'status']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return self.create_order(serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create_order(serializer):
        """ Логика создания заказа, если данные валидны. """
        try:
            order = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def revenue(self) -> Response:
        """
        Возвращает общую сумму выручки за оплаченные заказы.

        Выручка рассчитывается на основе всех заказов, имеющих статус `paid`.

        :return: JSON-ответ с суммарной выручкой.
        """
        revenue = Order.objects.filter(status='paid').aggregate(total_revenue=Sum('total_price'))
        return Response({'total_revenue': revenue['total_revenue'] or 0})
