from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from lcd.models import Lcd
from django.urls import reverse_lazy
from controller.main import get_ip_address


class Index(ListView):
    template_name = 'lcd/index.html'
    model = Lcd
    ordering = 'pk'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['page'] = 'lcd'
        context['title'] = 'lcd Index'
        return context


class LcdCreate(CreateView):
    model = Lcd
    template_name = 'lcd/create.html'
    fields = ['active', 'line_1', 'line_2', 'show_ip', 'ip_line', 'show_mode', 'mode_line', 'power_switch_pin']
    success_url = reverse_lazy('lcd:index')

    def get_context_data(self, **kwargs):
        context = super(LcdCreate, self).get_context_data(**kwargs)
        context['title'] = 'Create lcd'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if form.cleaned_data['active']:
            Lcd.objects.exclude(pk=self.kwargs['pk']).update(active=False)
        if form.cleaned_data['show_ip']:
            if form.cleaned_data['ip_line'] == 1:
                self.object.line_1 = "IP Address: " + get_ip_address()
            else:
                self.object.line_2 = "IP Address: " + get_ip_address()
        if form.cleaned_data['show_mode']:
            if form.cleaned_data['mode_line'] == 1:
                self.object.line_1 = "Mode"
            else:
                self.object.line_2 = "Mode"
        self.object.save()
        return super(LcdCreate, self).form_valid(form)


class LcdUpdate(UpdateView):
    model = Lcd
    template_name = 'lcd/update.html'
    fields = ['active', 'line_1', 'line_2', 'show_ip', 'ip_line', 'show_mode', 'mode_line', 'power_switch_pin']
    success_url = reverse_lazy('lcd:index')

    def get_context_data(self, **kwargs):
        context = super(LcdUpdate, self).get_context_data(**kwargs)
        context['title'] = 'Update lcd'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if form.cleaned_data['active']:
            Lcd.objects.exclude(pk=self.kwargs['pk']).update(active=False)
        if form.cleaned_data['show_ip']:
            if form.cleaned_data['ip_line'] == 1:
                self.object.line_1 = "IP Address: " + get_ip_address()
            else:
                self.object.line_2 = "IP Address: " + get_ip_address()
        if form.cleaned_data['show_mode']:
            if form.cleaned_data['mode_line'] == 1:
                self.object.line_1 = "Mode"
            else:
                self.object.line_2 = "Mode"
        self.object.save()
        return super(LcdUpdate, self).form_valid(form)


class LcdDelete(DeleteView):
    model = Lcd
    template_name = 'lcd/delete.html'
    success_url = reverse_lazy('lcd:index')

    def get_context_data(self, **kwargs):
        context = super(LcdDelete, self).get_context_data(**kwargs)
        context['title'] = 'Delete lcd'
        return context
