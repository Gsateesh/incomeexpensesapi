from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from expenses.models import Expense
from expenses.permissions import IsOwner
from .serializers import ExpensesSerializer
from rest_framework import permissions

# Create your views here.

class ExpenseListAPIView(ListCreateAPIView):
    serializer_class = ExpensesSerializer
    queryset=Expense.objects.all()
    permission_class = (permissions.IsAuthenticated, )

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

class ExpenseDetailsAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExpensesSerializer
    queryset=Expense.objects.all()
    permission_class = (permissions.IsAuthenticated, IsOwner)
    lookup_field = 'id'

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
