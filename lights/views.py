from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from lights.models import Light
from django.urls import reverse_lazy


class Index(ListView):
    template_name = 'lights/index.html'
    model = Light

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['page'] = 'lights'
        context['title'] = 'Light Index'
        return context


class LightCreate(CreateView):
    model = Light
    template_name = 'lights/create.html'
    fields = ['color', 'pin', 'delay', 'duration']
    success_url = reverse_lazy('lights:index')

    def get_context_data(self, **kwargs):
        context = super(LightCreate, self).get_context_data(**kwargs)
        context['title'] = 'Create Light'
        return context


class LightUpdate(UpdateView):
    model = Light
    template_name = 'lights/update.html'
    fields = ['color', 'pin', 'delay', 'duration']
    success_url = reverse_lazy('lights:index')

    def get_context_data(self, **kwargs):
        context = super(LightUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Update Light'
        return context

class LightDelete(DeleteView):
    model = Light
    template_name = 'lights/delete.html'
    success_url = reverse_lazy('lights:index')

    def get_context_data(self, **kwargs):
        context = super(LightDelete, self).get_context_data(**kwargs)
        context['title'] = 'Delete Light'
        return context
