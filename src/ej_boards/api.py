from rest_framework import viewsets
from rest_framework.response import Response
from ej.permissions import IsAuthenticatedOnlyGetView
from .models import Board
from .serializers import BoardDetailSerializer, BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticatedOnlyGetView]

    def retrieve(self, request, pk):
        board = self.get_object()
        return Response(BoardDetailSerializer(board).data)
