from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cart, Category, Order, OrderItem, Payment, Product, Shop, ShopUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    shop_id = serializers.IntegerField(source="category.shop.id", read_only=True)
    shop = serializers.CharField(source="category.shop.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "product_type",
            "price",
            "stock",
            "is_active",
            "shop_id",
            "category",
            "category_name",
            "shop",
        ]


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product", queryset=Product.objects.filter(is_active=True), write_only=True
    )

    class Meta:
        model = Cart
        fields = ["id", "product", "product_id", "quantity", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop_status = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price_at_purchase", "shop_status"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["payment_ref", "amount", "status", "verified_at", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "created_at", "items", "payment"]


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    shop_count = serializers.IntegerField()


class CategoryStatsSerializer(CategorySerializer):
    """Backward-compatible alias for category stats output."""


class ShopSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = [
            "id",
            "name",
            "description",
            "contact_phone",
            "upi_id",
            "image_url",
            "categories",
        ]

    def get_categories(self, obj):
        return list(obj.categories.values_list("name", flat=True).distinct())


class ShopLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ShopOrderStatusUpdateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.ChoiceField(
        choices=[
            OrderItem.SHOP_STATUS_PENDING,
            OrderItem.SHOP_STATUS_PREPARING,
            OrderItem.SHOP_STATUS_READY,
            OrderItem.SHOP_STATUS_AVAILABLE,
            OrderItem.SHOP_STATUS_COMPLETED,
        ]
    )


class ShopOrdersSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    customer = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    created_at = serializers.DateTimeField()
    items = OrderItemSerializer(many=True)


class ShopProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    current_category_id = serializers.IntegerField(source="category.id", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "product_type",
            "price",
            "stock",
            "is_active",
            "category_id",
            "current_category_id",
            "category_name",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        category = attrs.get("category") or getattr(self.instance, "category", None)
        if request and category:
            shop_user = (
                ShopUser.objects.filter(user=request.user)
                .select_related("shop")
                .first()
            )
            if not shop_user or category.shop_id != shop_user.shop_id:
                raise serializers.ValidationError("Category must belong to your shop.")
        return attrs


class ShopProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", "description", "contact_phone", "upi_id", "image_url"]

