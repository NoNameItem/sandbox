from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from snippetalk.forms import SnippetForm
from snippetalk.models import Snippet
from snippetalk.utils import LANGUAGE_CHOICES, LANG_JS, highlight, PLAIN_TEXT


def recent(request):
    snippets = Snippet.objects.filter(public=1).order_by('-modified')
    return render_to_response('snippetalk/list.html',
                              {
                                  'active_page': "recent",
                                  'snippets': snippets,
                                  'title': "Recent snippets"
                              },
                              RequestContext(request))


@login_required
def my(request):
    snippets = Snippet.objects.filter(author=request.user).order_by('-modified')
    return render_to_response('snippetalk/list.html',
                              {
                                  'active_page': "my",
                                  'snippets': snippets,
                                  'title': "My snippets"
                              },
                              RequestContext(request))


def create(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save()
            user = request.user
            if user.is_authenticated():
                snippet.author = user
                snippet.save()
            return JsonResponse(status=200, data={'link': "/snippetalk/{0}".format(snippet.id)})
        else:
            return JsonResponse(status=400, data={'message': 'Check fields', 'errorlist':
                form.errors})
    else:
        return JsonResponse(status=400, data={'message': 'Use POST'})


def show(request, snippet_id=None):

    try:
        snippet = Snippet.objects.get(id=snippet_id)
        mine = snippet.author == request.user
    except Snippet.DoesNotExist:
        snippet = None
        mine = True
    return render_to_response('snippetalk/snippet.html',
                              {
                                  'snippet': snippet,
                                  'mine': mine,
                                  'langs': LANG_JS,
                                  'plain_text': PLAIN_TEXT
                              },
                              RequestContext(request))


def get_highlight(request):
    if request.method == 'GET':
        l = int(request.GET['lang']) - 1
        lang_name = LANGUAGE_CHOICES[l][1]
        code = highlight(request.GET['code'], lang_name)
        return JsonResponse(status=200, data={'code': code})
    else:
        return JsonResponse(status=400, data={'message': "Use GET"})


def save(request):
    if request.method == 'POST':
        if request.POST['id']:
            try:
                snippet = Snippet.objects.get(id=int(request.POST['id']))
                new = SnippetForm(request.POST)
                if new.is_valid():
                    snippet.name = new.cleaned_data['name']
                    snippet.public = new.cleaned_data['public']
                    snippet.language = new.cleaned_data['language']
                    snippet.code = new.cleaned_data['code']
                    snippet.description = new.cleaned_data['description']
                    snippet.save()
                    return JsonResponse(status=200, data={'message': "OK",
                                                          'mod_time': snippet.modified})
                else:
                    return JsonResponse(status=401, data={'message': "Wrong POST data"})
            except Snippet.DoesNotExist:
                return JsonResponse(status=404, data={'message': "Snippet not found"})
        else:
            return create(request)
    else:
        return JsonResponse(status=400, data={'message': "Use POST"})


def delete(request, snippet_id):
    snippet = get_object_or_404(Snippet, id=snippet_id)
    snippet.delete()
    return HttpResponseRedirect('/snippetalk/')