from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Switch
from django.urls import reverse_lazy


class SwitchIndex(ListView):
    template_name = 'switches/index.html'
    model = Switch
    ordering = 'pk'

    def get_context_data(self, **kwargs):
        context = super(SwitchIndex, self).get_context_data(**kwargs)
        context['page'] = 'switches'
        context['title'] = 'Switch Index'
        return context


class SwitchCreate(CreateView):
    model = Switch
    template_name = 'switches/create.html'
    fields = ['name', 'pin', 'pull', 'on_name', 'off_name']
    success_url = reverse_lazy('switches:index')

    def get_context_data(self, **kwargs):
        context = super(SwitchCreate, self).get_context_data(**kwargs)
        context['title'] = 'Create Switch'
        return context


class SwitchUpdate(UpdateView):
    model = Switch
    template_name = 'switches/update.html'
    fields = ['name', 'pin', 'pull', 'on_name', 'off_name']
    success_url = reverse_lazy('switches:index')

    def get_context_data(self, **kwargs):
        context = super(SwitchUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Update Switch'
        return context


class SwitchDelete(DeleteView):
    model = Switch
    template_name = 'switches/delete.html'
    success_url = reverse_lazy('switches:index')

    def get_context_data(self, **kwargs):
        context = super(SwitchDelete, self).get_context_data(**kwargs)
        context['title'] = 'Delete Switch'
        return context
