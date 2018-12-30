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
        if Switch.objects.count() >= 2:
            context['add_disabled'] = True
        return context


class SwitchCreate(CreateView):
    model = Switch
    template_name = 'switches/create.html'
    fields = ['name', 'pin', 'pull', 'on_name', 'off_name', 'switch_type']
    success_url = reverse_lazy('switches:index')

    def get_context_data(self, **kwargs):
        context = super(SwitchCreate, self).get_context_data(**kwargs)
        context['title'] = 'Create Switch'
        return context

    def form_valid(self, form):
        if form.cleaned_data['switch_type']:
            other_switch = 0
        else:
            other_switch = 1
        switches = Switch.objects.all().update(switch_type=other_switch)
        return super(SwitchCreate, self).form_valid(form)


class SwitchUpdate(UpdateView):
    model = Switch
    template_name = 'switches/update.html'
    fields = ['name', 'pin', 'pull', 'on_name', 'off_name', 'switch_type']
    success_url = reverse_lazy('switches:index')

    def get_context_data(self, **kwargs):
        context = super(SwitchUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Update Switch'
        return context

    def form_valid(self, form):
        if form.cleaned_data['switch_type']:
            other_switch = 0
        else:
            other_switch = 1
        Switch.objects.all().exclude(pk=self.kwargs['pk']).update(switch_type=other_switch)
        return super(SwitchUpdate, self).form_valid(form)


class SwitchDelete(DeleteView):
    model = Switch
    template_name = 'switches/delete.html'
    success_url = reverse_lazy('switches:index')

    def get_context_data(self, **kwargs):
        context = super(SwitchDelete, self).get_context_data(**kwargs)
        context['title'] = 'Delete Switch'
        return context
