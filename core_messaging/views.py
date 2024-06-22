from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from .models import ChatThread, Chatmessage

User = get_user_model()

class ReceivedMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sender_id = request.user.id

        # Find all threads where the sender is the primary user
        threads = ChatThread.objects.filter(primary_user_id=sender_id)

        # Get all users who received messages from the sender
        receiver_ids = Chatmessage.objects.filter(
            thread__in=threads, user_id=sender_id
        ).values_list('thread__secondary_user', flat=True).distinct()

        # Fetch the receiver user details
        receivers = User.objects.filter(id__in=receiver_ids)
        receiver_data = [
            {"id": user.id, "firstname": user.first_name, "lastname": user.last_name, 'profile': user.profile}
            for user in receivers
        ]

        return Response(receiver_data, status=status.HTTP_200_OK)

