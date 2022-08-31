from rest_framework import generics


class ListOrRetrieveMixin(
    generics.RetrieveDestroyAPIView,
    generics.ListCreateAPIView
):
    pass
