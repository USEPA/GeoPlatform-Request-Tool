from django.contrib.contenttypes.models import ContentType


class ContentTypeListMixin(object):
    def list(self, request, *args, **kwargs):
        response = super(ContentTypeListMixin, self).list(request, *args, **kwargs)
        if 'results' not in response.data:
            response.data = {'results': response.data}
        response.data['content_type'] = ContentType.objects.get_for_model(self.queryset.model).id
        return response

