from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator


class Order(models.Model):
    """
    Модель заказа
    Включает в себя:
        table_number (int): Номер столика, должен быть больше или равен 1.
        items (List[Dict[str, Any]]): JSON-список блюд в заказе.
        total_price (Decimal): Общая сумма заказа.
        status (str): Статус заказа (waiting, ready, paid).
    """
    STATUS_CHOICES = [
        ('waiting', 'в ожидании'),
        ('ready', 'готово'),
        ('paid', 'оплачено'),
    ]
    table_number = models.IntegerField(validators=[MinValueValidator(1)])
    items = models.JSONField(default=list)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')

    def clean(self) -> None:
        """
        Валидация данных:
        1. Поле items не может быть пустым.
        2. Цена не может быть нулевой или отрицательной.
        3. Статус должен быть валидным.
        """
        if not self.items:
            raise ValidationError("Поле 'items' не может быть пустым.")

        for item in self.items:
            if item.get('price') <= 0:
                raise ValidationError("Цена блюда не может быть отрицательной или нулевой.")
            if not item.get('name'):
                raise ValidationError("Название блюда не может быть пустым.")

        if self.status not in dict(self.STATUS_CHOICES):
            raise ValidationError(f"Некорректный статус: {self.status}.")

    def save(self, *args, **kwargs) -> None:
        """
        Перед сохранением заказа автоматически вычисляем total_price как сумму цен всех блюд,
        а также проверяем данные на валидность.
        """
        if self.total_price is None:
            self.total_price = sum(item.get('price', 0) for item in self.items)

        # Проверяем на валидность перед сохранением
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ {self.id} - Столик {self.table_number} - Сумма {self.total_price}"
