"""
Views for porticus
"""
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import ImproperlyConfigured

from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import BaseListView

from porticus.models import Gallery, Album, Ressource


class SimpleListView(TemplateResponseMixin, BaseListView):
    """
    Like generic.ListView but use only ``get_template`` to find template and not an
    automatic process on ``get_template_names``
    
    paginate_by = settings.PORTICUS_PAGINATION
    get_queryset()
    template_name || get_template()
    model = ...
    """
    pass


class DetailListView(SimpleListView):
    """
    Get a child list from an object
    """
    detail_model = None
    context_parent_object_name = 'detail_object'

    def get_detail_object(self):
        if self.detail_model is None:
            raise ImproperlyConfigured(u"%(cls)s's 'detail_model' class attribute must be defined " % {"cls": self.__class__.__name__})
        return get_object_or_404(self.detail_model, slug=self.kwargs.get('detail_slug'))

    def get(self, request, *args, **kwargs):
        self.detail_object = self.get_detail_object()
        return super(DetailListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({
            self.context_parent_object_name: self.detail_object,
        })
        return super(DetailListView, self).get_context_data(**kwargs)


class GalleryListView(SimpleListView):
    paginate_by = settings.PORTICUS_PAGINATION
    model = Gallery
    template_name = "porticus/gallery_list.html"


class GalleryDetailView(DetailListView):
    detail_model = Gallery
    context_parent_object_name = 'gallery_object'
    
    model = Album
    paginate_by = settings.PORTICUS_PAGINATION

    def get_queryset(self):
        # TODO: use the correct manager
        return self.detail_object.album_set.all().order_by('priority', 'name')
    
    def get_template_names(self):
        return (self.detail_object.template_name,)


class AlbumDetailView(DetailListView):
    detail_model = Album
    context_parent_object_name = 'album_object'
    
    model = Ressource
    paginate_by = settings.PORTICUS_PAGINATION

    def get_detail_object(self):
        self.gallery_object = get_object_or_404(Gallery, slug=self.kwargs.get('parent_slug'))
        return super(AlbumDetailView, self).get_detail_object()

    def get_queryset(self):
        return self.detail_object.ressource_set.all().order_by('priority', 'name')

    def get_context_data(self, **kwargs):
        kwargs.update({
            'gallery_object': self.gallery_object,
        })
        return super(AlbumDetailView, self).get_context_data(**kwargs)
    
    def get_template_names(self):
        return (self.detail_object.template_name,)
