from gettext import translation
import json
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from .forms import TranslateForm
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import activate
from base import mods


def get_context_data(request, voting_id):
    template = loader.get_template('visualizer/visualizer.html')
    context = {}

    formulario = TranslateForm()

    try:
        r = mods.get('voting', params={'id': voting_id})
        context['voting'] = json.dumps(r[0])

        if r[0]['question']['multioption']:
            postpro = r[0]['postproc']
            position_votes = {}
            for i,votes in enumerate(postpro):
                position_votes[i] = votes['votes']

            sorted_votes = dict(sorted(position_votes.items(), key=lambda item:item[1]))
            order = list(sorted_votes.values())

            for index,key in enumerate(sorted_votes.keys()):
                order[key] = index+1
            context['order'] = order
            for index in range(0,len(r[0]['postproc'])):
                r[0]['postproc'][index]['order'] = order[index]
            context['voting'] = json.dumps(r[0])

        if request.method == 'POST':
            formulario = TranslateForm(request.POST)
            if formulario.is_valid():
                language = formulario.cleaned_data['language']
                activate(language)

        context['formulario'] = formulario

    except:
        raise Http404

    return HttpResponse(template.render(context, request))
