from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response


def method_not_allowed(f):
    response = {'message': '{} method not allowed in this path.'.format(f)}
    return Response(response, status=405)


class CustomModelViewSet(ModelViewSet):
    methods = []

    def retrieve(self, request, *args, **kwargs) -> Response:
        if 'retrieve' not in self.methods:
            return method_not_allowed('Retrieve')
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs) -> Response:
        if 'list' not in self.methods:
            return method_not_allowed('List')
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs) -> Response:
        if 'create' not in self.methods:
            return method_not_allowed('Create')
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:
        if 'update' not in self.methods:
            return method_not_allowed('Update')
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs) -> Response:
        if 'partial_update' not in self.methods:
            return method_not_allowed('Partial update')
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        if 'destroy' not in self.methods:
            return method_not_allowed('Destroy')
        return super().destroy(request, *args, **kwargs)
