from django import forms
from django import forms
from django.core.exceptions import ValidationError
from .models import Order


class OrderForm(forms.ModelForm):
    """
    Форма для создания и редактирования заказа.
    Включает номер стола, статус заказа, названия и цены блюда, а также итоговую сумму.
    """
    total_price = forms.CharField(
        label="Итоговая сумма",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    dish_price = forms.CharField(
        label='Цена блюда',
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    dish_name = forms.CharField()

    class Meta:
        model = Order
        fields = ['table_number', 'status']
        exclude = ('total_price',)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.items:
            self.fields['total_price'].initial = sum(item['price'] for item in self.instance.items)
            self.dishes = self.instance.items

    def clean_table_number(self) -> int:
        """
        Проверяет, что номер стола не меньше 1.
        :return: Номер стола.
        :raises ValidationError: Если номер стола меньше 1.
        """
        table_number = self.cleaned_data.get('table_number')
        if table_number is not None and table_number < 1:
            raise ValidationError('Номер стола не может быть меньше 1')
        return table_number

    def clean(self) -> dict:
        """
        Проверяет, что названия и цены блюда валидные и вообще переданы, а также вычисляет общую сумму заказа.
        :return: Словарь с обработанными данными.
        """
        cleaned_data = super().clean()

        try:
            # Если данные пришли не в QueryDict, а в обычном словаре
            if isinstance(self.data, dict):
                dish_names = self.data['dish_name']
                dish_prices = [self.data['dish_price']] if isinstance(self.data.get('dish_price'),
                                                                      (float, str, int)) else \
                    self.data[
                        'dish_price']
            else:
                dish_names = self.data.getlist('dish_name')
                dish_prices = self.data.getlist('dish_price')
        except Exception as e:
            raise ValidationError("В заказе должно быть хотя бы одно блюдо")

        if not dish_names or not dish_prices:
            raise ValidationError("Названия или цены блюд не могут быть пустыми.")

        # Проверяем название и цену каждого блюда
        items = []
        for name, price in zip(dish_names, dish_prices):
            if not name.strip():
                raise ValidationError({'dish_name': 'Название блюда не может быть пустым.'})
            try:
                price = float(price)
                if price <= 0:
                    raise ValidationError({'dish_price': 'Цена блюда не может быть меньше или равна нулю.'})
            except ValueError:
                raise ValidationError({'dish_price': 'Цена блюда должна быть числом.'})
            items.append({"name": name, "price": price})

        self.instance.items = items
        total_price = sum(item['price'] for item in items)
        self.instance.total_price = total_price

        self.fields['total_price'].initial = total_price

        return cleaned_data


class OrderSearchForm(forms.Form):
    table_number = forms.IntegerField(
        label="Номер стола",
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Введите номер стола'})
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[
            ('', 'Все статусы'),
            ('waiting', 'В ожидании'),
            ('ready', 'Готово'),
            ('paid', 'Оплачено'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
