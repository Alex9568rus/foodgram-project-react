from django.db.models import Sum
from django.utils import timezone

from recipes.models import IngredientRecipe


def format_shopping_list(user):
    ingredients = (
        IngredientRecipe.objects.filter(recipe__cart__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount=Sum('amount'))
    )
    local_time = timezone.localtime().strftime("%d/%m/%Y %H:%M")
    shopping_list = f'Список покупок {user.first_name} {local_time}\n\n'
    for ingredient in ingredients:
        shopping_list += (
            f'{ingredient["ingredient__name"]}: {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}\n'
        )
    shopping_list += '\nFoodgram'
    return shopping_list
