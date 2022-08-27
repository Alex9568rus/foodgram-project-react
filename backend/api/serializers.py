from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from api.models import (
    Cart, FavoriteRecipe, IngredienInRecipe, Ingredient, Recipe, Tag
)
from users.models import User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class TagsField(serializers.SlugRelatedField):

    def to_representation(self, obj):
        request = self.context.get('request')
        context = {'request': request}
        serializer = TagSerializer(obj, context=context)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredienInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredienInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=IngredienInRecipe.objects.all(),
                fields=('ingredient', 'recipe')
            ),
        )
    
    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredienInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagsField(
        slug_field='id', queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredienInRecipeSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def in_favorite_or_cart(self, obj, model):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.in_favorite_or_cart(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self.in_favorite_or_cart(obj, Cart)


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError(
                'Нужно добавить ингредиент'
            )
        ingredients_list = []
        for ingredient in data:
            id = ingredient['id']
            if id in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиент уже есть в списке'
                )
            ingredients_list.append(id)
            amount = ingredient['amount']
            if int(amount) > 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть >= 1'
                )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                'Нужно дабавить тег'
            )
        tag_list = []
        for tag in data:
            if tag in tag_list:
                raise serializers.ValidationError(
                    'Такой тег уже добавлен'
                )
            tag_list.append(tag)
        return data

    def validate_cooking_time(self, data):
        if int(data) < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть >= 1 мин'
            )
        return data

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            id = ingredient['id']
            amount = ingredient['amount']
            IngredienInRecipe.objects.bulk_create(
                [
                    IngredienInRecipe(
                        ingredient=id, recipe=recipe, amount=amount
                    ),
                ]
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self.add_ingredients(ingredients, instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe'],
                message='Данный рецепт уже в избранном'
            ),
        ]


class CartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe'],
                message='Данный рецепт уже в корзине'
            ),
        ]
