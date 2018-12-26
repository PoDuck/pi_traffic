from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['page'] = 'home'
        context['title'] = 'Home'
        return context
