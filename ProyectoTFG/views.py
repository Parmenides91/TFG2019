from typing import Dict, Any

from django.views.generic import TemplateView

from datetime import datetime, timedelta

class TestPage(TemplateView):
    template_name = 'test.html'

class ThanksPage(TemplateView):
    template_name = 'thanks.html'

class HomePage(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        now = datetime.now().__format__('%Y-%m-%d')
        """
        principio = now + 'T02:00:00'
        finalYear = datetime.now().__format__('%Y')
        finalMonth = datetime.now().__format__('%m')
        finalDay = datetime.now().__format__('%d')
        final = datetime(int(finalYear), int(finalMonth), int(finalDay), 1, 0, 0)
        final += timedelta(days=1)
        final = final.isoformat('T')
        context['inicio_fecha'] = principio
        context['final_fecha'] = final
        """
        context = super().get_context_data(**kwargs)
        context['index_fecha'] = now
        return context
