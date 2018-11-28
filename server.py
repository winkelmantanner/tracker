import sys
import pickle

import file_tree_loader

from django.conf import settings
from django.conf.urls import url
from django.core.management import execute_from_command_line
from django.views import View
from django.http import HttpResponse

STATE_NAME_KEY = 'state_name'
FILE_DICT_KEY = 'file_dict'


class Index(View):
    def get(self, request):
        return HttpResponse('<h1>A minimal Django response!</h1>')
    def post(self, request):
        data = pickle.loads(request.body)
        state_name = data[STATE_NAME_KEY]
        file_dict = data[FILE_DICT_KEY]
        save_result = file_tree_loader.save_dict(state_name, file_dict)
        return HttpResponse(save_result)

urlpatterns = [
    url(r'^$', Index.as_view()),
]

if __name__ == '__main__':
    settings.configure(
        DEBUG=False,
        ROOT_URLCONF=sys.modules[__name__],
    )
    execute_from_command_line(sys.argv + ['runserver'])