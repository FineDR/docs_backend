from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status as drf_status
from .models import Order
from .serializers import OrderSerializer

# Create order
class CreateExportOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cv_id = request.data.get('cvId')
        if not cv_id:
            return Response({'error': 'cvId required'}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Prevent multiple pending orders for the same CV
        existing_order = Order.objects.filter(
            user=request.user,
            cv_id=cv_id,
            status='pending'
        ).first()
        if existing_order:
            serializer = OrderSerializer(existing_order)
            return Response({'message': 'Pending order already exists', 'order': serializer.data})

        order = Order.objects.create(user=request.user, cv_id=cv_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# Initiate payment
class InitiatePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('orderId')
        phone = request.data.get('phone')
        provider = request.data.get('provider')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        if order.status != 'pending':
            return Response({'error': 'Order not payable'}, status=drf_status.HTTP_400_BAD_REQUEST)

        # Format phone
        if phone.startswith('0'):
            phone = '+255' + phone[1:]
        elif not phone.startswith('+255'):
            phone = '+255' + phone

        # Integrate Selcom/Flutterwave API here
        payment_ref = f"{provider.upper()}-{order.id}"
        checkout_url = None  # Optional

        order.provider = provider
        order.provider_ref = payment_ref
        order.save()

        return Response({'paymentRef': payment_ref, 'checkoutUrl': checkout_url})


# Check order status
class OrderStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=drf_status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)


# Webhook endpoint (no auth)
class PaymentWebhook(APIView):
    permission_classes = []

    def post(self, request):
        # TODO: verify provider signature for security
        event = request.data
        reference = event.get('reference')
        status_event = event.get('status')

        try:
            order = Order.objects.get(provider_ref=reference)
        except Order.DoesNotExist:
            return Response(status=200)  # idempotent

        if status_event in ['paid', 'successful', 'success']:
            order.status = 'paid'
            order.transaction_id = event.get('transaction_id') or ''
        elif status_event in ['failed', 'cancelled']:
            order.status = 'failed'

        order.save()
        return Response(status=200)


# Paid-check endpoint for frontend
class CheckPaidOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cv_id):
        paid_order = Order.objects.filter(
            user=request.user,
            cv_id=cv_id,
            status='paid'
        ).order_by('-created_at').first()

        if not paid_order:
            return Response({'error': 'Payment required'}, status=402)

        serializer = OrderSerializer(paid_order)
        return Response(serializer.data)
