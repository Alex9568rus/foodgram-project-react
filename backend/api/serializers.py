from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import IngredientRecipe, Ingredient, Recipe, Tag
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exist()


#class TagsField(serializers.SlugRelatedField):
#
#    def to_representation(self, obj):
#        request = self.context.get('request')
#        context = {'request': request}
#        serializer = TagSerializer(obj, context=context)
#        return serializer.data


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = SimpleRecipeSerializer
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exist()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = (
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
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
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_in_recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exist() 

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.cart.filter(recipe=obj).exist()


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(use_url=True)
    #author = UserSerializer(read_only=True)
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
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
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
        self.add_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)


#class FavoriteSerializer(serializers.ModelSerializer):
#    recipe = serializers.PrimaryKeyRelatedField(
#        queryset=Recipe.objects.all()
#    )
#    user = serializers.PrimaryKeyRelatedField(
#        queryset=User.objects.all()
#    )
#
#    class Meta:
#        model = FavoriteRecipe
#        fields = '__all__'
#        validators = [
#            UniqueTogetherValidator(
#                queryset=FavoriteRecipe.objects.all(),
#                fields=['user', 'recipe'],
#                message='Данный рецепт уже в избранном'
#            ),
#        ]
#
#
#class CartSerializer(serializers.ModelSerializer):
#    recipe = serializers.PrimaryKeyRelatedField(
#        queryset=Recipe.objects.all()
#    )
#    user = serializers.PrimaryKeyRelatedField(
#        queryset=User.objects.all()
#    )
#
#    class Meta:
#        model = FavoriteRecipe
#        fields = '__all__'
#        validators = [
#            UniqueTogetherValidator(
#                queryset=FavoriteRecipe.objects.all(),
#                fields=['user', 'recipe'],
#                message='Данный рецепт уже в корзине'
#            ),
#        ]
