from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from core.serializers import CurrentDateSerializer


class BulkCreateUpdateAPIView(GenericAPIView):
    pk_field_name = "id"

    def post(self, request, *args, **kwargs):
        data = request.data
        response_data = []
        for item in data:
            try:
                id = item.get(self.pk_field_name)
            except AttributeError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            try:
                object = self.get_serializer_class().Meta.model.objects.get(pk=id)
                serializer = self.get_serializer(object, data=item)
            except self.get_serializer_class().Meta.model.DoesNotExist:
                serializer = self.get_serializer(data=item)
            except ValidationError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                serializer.save()
                if id in [item[self.pk_field_name] for item in response_data]:
                    response_data = list(
                        filter(lambda x: x[self.pk_field_name] != id, response_data)
                    )
                response_data.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_201_CREATED)


class DateSetView(CreateAPIView):
    serializer_class = CurrentDateSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.status_code = 200
        return response
