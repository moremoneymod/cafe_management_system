from typing import Any
from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели заказа.

    Поля:
    - `id` (int): Уникальный идентификатор заказа.
    - `table_number` (int): Номер столика, за которым сделан заказ.
    - `items` (list[dict]): Список блюд в заказе.
    - `status` (str): Статус заказа (`pending`, `paid`, `canceled` и т. д.).
    """

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'items', 'status', 'total_price']  # `total_price` исключен

    def validate_items(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Проверяет, что цена каждого блюда в заказе не отрицательная.

        :param value: Список блюд, содержащих информацию о цене.
        :raises serializers.ValidationError: Если хотя бы одно блюдо имеет отрицательную цену.
        :return: Исходный список, если валидация пройдена.
        """
        if not value:
            raise serializers.ValidationError("Поле 'items' не может быть пустым.")
        for item in value:
            if item.get('price') <= 0:
                raise serializers.ValidationError('Цена блюда не может быть меньше или равна нулю.')
            if not item.get('name'):
                raise serializers.ValidationError('Название блюда не может быть пустым.')
        return value

    def create(self, validated_data: dict[str, Any]) -> Order:
        """
        Создает новый заказ, автоматически вычисляя `total_price`.

        `total_price` рассчитывается как сумма цен всех блюд в заказе.

        :param validated_data: Данные, прошедшие валидацию.
        :return: Экземпляр модели `Order`.
        """
        items = validated_data.get('items')
        if not items:
            raise serializers.ValidationError('Поле "items" не может быть пустым.')
        validated_data['total_price'] = sum(item.get('price', 0) for item in items)
        return super().create(validated_data)

    def update(self, instance: Order, validated_data: dict[str, Any]) -> Order:
        """
        Обновляет заказ, автоматически пересчитывая `total_price`.

        `total_price` обновляется, если в запросе передан список `items`.

        :param instance: Существующий экземпляр заказа.
        :param validated_data: Обновленные данные.
        :return: Обновленный экземпляр `Order`.
        """
        if 'items' in validated_data:
            items = validated_data['items']
            instance.total_price = sum(item.get('price', 0) for item in items)
        return super().update(instance, validated_data)
