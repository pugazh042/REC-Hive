from decimal import Decimal

from django.contrib.auth import authenticate
from django.db import models, transaction
from django.db.models import F, Sum, DecimalField
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, Category, Order, OrderItem, Payment, Product, Shop, ShopUser
from .serializers import (
    CategorySerializer,
    CartSerializer,
    LoginSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductSerializer,
    RegisterSerializer,
    ShopProfileSerializer,
    ShopProductSerializer,
    ShopSerializer,
    ShopLoginSerializer,
    ShopOrderStatusUpdateSerializer,
    UserProfileSerializer,
)


# -------------------------
# USER REGISTER
# -------------------------
class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer

    permission_classes = [permissions.AllowAny]


    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(

            {

                "user": RegisterSerializer(user).data,

                "token": token.key,

            },

            status=status.HTTP_201_CREATED,

        )


# -------------------------
# USER LOGIN
# -------------------------
class LoginView(APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = authenticate(

            username=serializer.validated_data["username"],

            password=serializer.validated_data["password"],

        )

        if not user:

            return Response(

                {"detail": "Invalid username or password"},

                status=status.HTTP_401_UNAUTHORIZED,

            )


        token, _ = Token.objects.get_or_create(user=user)


        return Response({"token": token.key})

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# -------------------------
# SHOP LIST
# -------------------------
class ShopListView(APIView):

    permission_classes = [permissions.AllowAny]


    def get(self, request):
        shops = Shop.objects.all().order_by("name")
        category = request.query_params.get("category")
        if category:
            shops = shops.filter(categories__name__iexact=category).distinct()
        return Response(ShopSerializer(shops, many=True).data)


class CategoryListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = (
            Category.objects.values("name")
            .order_by("name")
            .annotate(shop_count=models.Count("shop", distinct=True))
        )
        return Response(CategorySerializer(categories, many=True).data)


# -------------------------
# PRODUCT LIST
# filter by shop
# -------------------------
class ProductListView(generics.ListAPIView):

    serializer_class = ProductSerializer

    permission_classes = [permissions.AllowAny]


    def get_queryset(self):

        queryset = Product.objects.filter(

            is_active=True

        ).select_related("category__shop")


        shop_id = self.request.query_params.get("shop_id")


        if shop_id:

            queryset = queryset.filter(

                category__shop_id=shop_id

            )


        return queryset


# -------------------------
# CART
# -------------------------
class CartView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):

        items = Cart.objects.filter(

            user=request.user

        ).select_related("product__category__shop")


        return Response(

            CartSerializer(items, many=True).data

        )


    def post(self, request):

        serializer = CartSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)


        product = serializer.validated_data["product"]

        quantity = serializer.validated_data["quantity"]


        item, created = Cart.objects.get_or_create(

            user=request.user,

            product=product,

            defaults={"quantity": quantity},

        )


        if not created:

            item.quantity += quantity

            item.save(update_fields=["quantity"])


        return Response(

            CartSerializer(item).data,

            status=status.HTTP_201_CREATED,

        )


    def delete(self, request):

        cart_id = request.data.get("cart_id")


        if not cart_id:

            return Response(

                {"detail": "cart_id required"},

                status=status.HTTP_400_BAD_REQUEST,

            )


        deleted, _ = Cart.objects.filter(

            id=cart_id,

            user=request.user,

        ).delete()


        if not deleted:

            return Response(

                {"detail": "Cart item not found"},

                status=status.HTTP_404_NOT_FOUND,

            )


        return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------
# CREATE ORDER FROM CART
# -------------------------
class OrderView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):

        orders = Order.objects.filter(

            user=request.user

        ).prefetch_related(

            "items__product__category__shop",

            "payment",

        )


        return Response(

            OrderSerializer(orders, many=True).data

        )


    @transaction.atomic

    def post(self, request):

        cart_items = Cart.objects.select_related(

            "product__category__shop"

        ).filter(

            user=request.user

        )


        if not cart_items.exists():

            return Response(

                {"detail": "Cart empty"},

                status=status.HTTP_400_BAD_REQUEST,

            )


        order = Order.objects.create(

            user=request.user,

            status=Order.STATUS_PENDING,

        )


        total = Decimal("0.00")


        for cart_item in cart_items:

            product = cart_item.product

            qty = cart_item.quantity


            if qty > product.stock:

                return Response(

                    {

                        "detail":

                        f"Stock not enough for {product.name}"

                    },

                    status=status.HTTP_400_BAD_REQUEST,

                )


            OrderItem.objects.create(

                order=order,

                product=product,

                quantity=qty,

                price_at_purchase=product.price,

            )


            product.stock -= qty

            product.save(update_fields=["stock"])


            total += product.price * qty


        order.total_amount = total

        order.save(update_fields=["total_amount"])


        Payment.objects.create(

            order=order,

            payment_ref=f"ORD-{order.id}",

            amount=total,

            status=Payment.STATUS_PENDING,

        )


        cart_items.delete()


        return Response(

            OrderSerializer(order).data,

            status=status.HTTP_201_CREATED,

        )


class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        items = request.data.get("items", [])
        is_paid_confirmed = bool(request.data.get("is_paid_confirmed", False))
        payment_ref = str(request.data.get("payment_ref", "")).strip()
        if not isinstance(items, list) or not items:
            return Response(
                {"detail": "items list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not is_paid_confirmed:
            return Response(
                {"detail": "Confirm payment before placing order"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(payment_ref) < 4:
            return Response(
                {"detail": "Valid payment_ref is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.create(user=request.user, status=Order.STATUS_PENDING)
        total = Decimal("0.00")

        for row in items:
            product_id = row.get("product_id")
            quantity = int(row.get("quantity", 1))

            if not product_id or quantity < 1:
                return Response(
                    {"detail": "Each item needs valid product_id and quantity"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            product = Product.objects.filter(id=product_id, is_active=True).first()
            if not product:
                return Response(
                    {"detail": f"Invalid product_id: {product_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if quantity > product.stock:
                return Response(
                    {"detail": f"Insufficient stock for product: {product.name}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price,
            )
            product.stock -= quantity
            product.save(update_fields=["stock"])
            total += product.price * quantity

        order.total_amount = total
        order.save(update_fields=["total_amount"])

        Payment.objects.create(
            order=order,
            payment_ref=payment_ref,
            amount=total,
            status=Payment.STATUS_PENDING,
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


# -------------------------
# PAYMENT VERIFY (UPI)
# -------------------------
class PaymentVerificationView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    @transaction.atomic

    def post(self, request):

        order_id = request.data.get("order_id")
        payment_ref = request.data.get("payment_ref")

        success = bool(

            request.data.get("success", False)

        )


        payment_qs = Payment.objects.filter(order__user=request.user)
        payment = payment_qs.filter(order_id=order_id).first() if order_id else None
        if not payment and payment_ref:
            payment = payment_qs.filter(payment_ref=payment_ref).first()


        if not payment:

            return Response(

                {"detail": "Payment not found"},

                status=status.HTTP_404_NOT_FOUND,

            )


        if success:

            payment.status = Payment.STATUS_VERIFIED

            payment.verified_at = timezone.now()


            payment.order.status = Order.STATUS_PAID

            payment.order.save(update_fields=["status"])


        else:

            payment.status = Payment.STATUS_FAILED


            payment.order.status = Order.STATUS_CANCELLED

            payment.order.save(update_fields=["status"])


        payment.save(update_fields=["status", "verified_at"])


        return Response(

            {

                "detail": "payment updated",

                "status": payment.status,

            }

        )


# -------------------------
# SHOP LOGIN
# -------------------------
class ShopLoginView(APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serializer = ShopLoginSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)


        user = authenticate(

            username=serializer.validated_data["username"],

            password=serializer.validated_data["password"],

        )


        if not user:

            return Response(

                {"detail": "Invalid login"},

                status=status.HTTP_401_UNAUTHORIZED,

            )


        if not ShopUser.objects.filter(user=user).exists():

            return Response(

                {"detail": "Not a shop account"},

                status=status.HTTP_403_FORBIDDEN,

            )


        token, _ = Token.objects.get_or_create(user=user)


        return Response({"token": token.key})


# -------------------------
# SHOP VIEW ORDERS
# shows only that shop's items
# -------------------------
class ShopOrdersView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):

        shop_user = ShopUser.objects.filter(

            user=request.user

        ).select_related("shop").first()


        if not shop_user:

            return Response(

                {"detail": "Shop login required"},

                status=status.HTTP_403_FORBIDDEN,

            )


        items = OrderItem.objects.select_related(

            "order__user",

            "product__category__shop",

        ).filter(

            product__category__shop=shop_user.shop

        ).order_by("-order__created_at")


        grouped = {}
        for item in items:
            if item.order_id not in grouped:
                grouped[item.order_id] = {
                    "order_id": item.order_id,
                    "customer": item.order.user.username,
                    "created_at": item.order.created_at,
                    "total_amount": item.order.total_amount,
                    "items": [],
                }
            grouped[item.order_id]["items"].append(item)

        data = []
        for row in grouped.values():
            data.append(
                {
                    "order_id": row["order_id"],
                    "customer": row["customer"],
                    "created_at": row["created_at"],
                    "total_amount": row["total_amount"],
                    "items": OrderItemSerializer(row["items"], many=True).data,
                }
            )
        return Response(data)


# -------------------------
# SHOP UPDATE STATUS
# -------------------------
class ShopUpdateOrderStatusView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    @transaction.atomic

    def post(self, request):

        shop_user = ShopUser.objects.filter(

            user=request.user

        ).select_related("shop").first()


        if not shop_user:

            return Response(

                {"detail": "Shop login required"},

                status=status.HTTP_403_FORBIDDEN,

            )


        serializer = ShopOrderStatusUpdateSerializer(

            data=request.data

        )

        serializer.is_valid(raise_exception=True)


        order_id = serializer.validated_data["order_id"]

        target_status = serializer.validated_data["status"]


        items = OrderItem.objects.filter(

            order_id=order_id,

            product__category__shop=shop_user.shop,

        ).select_related("product")


        if not items.exists():

            return Response(

                {"detail": "Order not found"},

                status=status.HTTP_404_NOT_FOUND,

            )


        for item in items:


            if item.product.product_type == Product.TYPE_FOOD:

                allowed = {

                    OrderItem.SHOP_STATUS_PENDING:

                        [OrderItem.SHOP_STATUS_PREPARING],

                    OrderItem.SHOP_STATUS_PREPARING:

                        [OrderItem.SHOP_STATUS_READY],

                    OrderItem.SHOP_STATUS_READY:

                        [OrderItem.SHOP_STATUS_COMPLETED],

                }


            else:

                allowed = {

                    OrderItem.SHOP_STATUS_PENDING:

                        [OrderItem.SHOP_STATUS_AVAILABLE],

                    OrderItem.SHOP_STATUS_AVAILABLE:

                        [OrderItem.SHOP_STATUS_COMPLETED],

                }


            if target_status not in allowed.get(

                item.shop_status,

                [],

            ):

                return Response(

                    {

                        "detail":

                        f"Invalid status change for {item.product.name}"

                    },

                    status=status.HTTP_400_BAD_REQUEST,

                )


        items.update(shop_status=target_status)


        return Response(

            {

                "detail": "status updated",

                "status": target_status,

            }

        )


class ShopDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop_user = ShopUser.objects.filter(user=request.user).select_related("shop").first()
        if not shop_user:
            return Response({"detail": "Shop login required"}, status=status.HTTP_403_FORBIDDEN)

        items = OrderItem.objects.filter(product__category__shop=shop_user.shop)
        pending_orders = items.filter(
            shop_status__in=[OrderItem.SHOP_STATUS_PENDING, OrderItem.SHOP_STATUS_PREPARING]
        ).values("order_id").distinct().count()
        completed_orders = items.filter(
            shop_status=OrderItem.SHOP_STATUS_COMPLETED
        ).values("order_id").distinct().count()
        low_stock = Product.objects.filter(category__shop=shop_user.shop, stock__lte=5).count()
        total_revenue = (
            items.filter(order__status=Order.STATUS_PAID).aggregate(
                total=Sum(
                    F("price_at_purchase") * F("quantity"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .get("total")
            or Decimal("0.00")
        )
        return Response(
            {
                "shop": ShopProfileSerializer(shop_user.shop).data,
                "stats": {
                    "pending_orders": pending_orders,
                    "completed_orders": completed_orders,
                    "low_stock_items": low_stock,
                    "total_revenue": total_revenue,
                },
            }
        )


class ShopProductListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_shop_user(self, request):
        return ShopUser.objects.filter(user=request.user).select_related("shop").first()

    def get(self, request):
        shop_user = self.get_shop_user(request)
        if not shop_user:
            return Response({"detail": "Shop login required"}, status=status.HTTP_403_FORBIDDEN)
        products = Product.objects.filter(category__shop=shop_user.shop).select_related("category")
        return Response(ShopProductSerializer(products, many=True).data)

    def post(self, request):
        shop_user = self.get_shop_user(request)
        if not shop_user:
            return Response({"detail": "Shop login required"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ShopProductSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ShopProductSerializer(product).data, status=status.HTTP_201_CREATED)


class ShopProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, product_id):
        return (
            Product.objects.select_related("category__shop")
            .filter(id=product_id, category__shop__shop_users__user=request.user)
            .first()
        )

    def put(self, request, product_id):
        product = self.get_object(request, product_id)
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShopProductSerializer(product, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, product_id):
        product = self.get_object(request, product_id)
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shop_user = ShopUser.objects.filter(user=request.user).select_related("shop").first()
        if not shop_user:
            return Response({"detail": "Shop login required"}, status=status.HTTP_403_FORBIDDEN)
        return Response(ShopProfileSerializer(shop_user.shop).data)

    def put(self, request):
        shop_user = ShopUser.objects.filter(user=request.user).select_related("shop").first()
        if not shop_user:
            return Response({"detail": "Shop login required"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ShopProfileSerializer(shop_user.shop, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)