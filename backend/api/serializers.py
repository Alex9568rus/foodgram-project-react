from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import (
    IngredientRecipe, Ingredient, Recipe,
    Tag, Favorite, ShoppingCart
)
from users.models import Follow, User


class CreateUserSerializer(UserCreateSerializer):
    # email = serializers.EmailField(
    #     validators=[
    #         UniqueValidator(queryset=User.objects.all()),
    #     ]
    # )
    # username = serializers.CharField(
    #     validators=[
    #         UniqueValidator(queryset=User.objects.all()),
    #     ]
    # )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'first_name', 'last_name'
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return user.follower.filter(author=obj).exists()


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
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField(use_url=True)
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True,
        source='recipe_ingredient'
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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exist()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exist()


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
            'tags', 'author', 'ingredients', 'name',
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
            IngredientRecipe.objects.bulk_create(
                [IngredientRecipe(
                    ingredient=id, recipe=recipe, amount=amount
                ), ]
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, **validated_data)
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.add_ingredients(ingredients, instance)
        instance.save()
        return instance


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Данный рецепт уже в избранном'
            ),
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Данный рецепт уже в корзине'
            ),
        ]


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return SimpleRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
