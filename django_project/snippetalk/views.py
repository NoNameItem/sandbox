import json
import os
import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render_to_response
from django.template import RequestContext

from snippetalk.forms import SnippetForm, FileForm
from snippetalk.models import Snippet, Comment
from snippetalk.utils import LANGUAGE_CHOICES, LANG_JS, highlight, PLAIN_TEXT, parse_filename


# url regex from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
URL_REGEX = re.compile(r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s\
()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')


def wrap_links(text):
    return URL_REGEX.sub(lambda x: '<a href="{0}">{0}</a>'.format(x.group(0)), text)


def recent(request):
    snippets = Snippet.objects.filter(public=1).order_by('-modified')
    return render_to_response('snippetalk/list.html',
                              {
                                  'active_page': "recent",
                                  'snippets':    snippets,
                                  'title':       "Recent snippets"
                              },
                              RequestContext(request))


@login_required
def my(request):
    snippets = Snippet.objects.filter(author=request.user).order_by('-modified')
    return render_to_response('snippetalk/list.html',
                              {
                                  'active_page': "my",
                                  'snippets':    snippets,
                                  'title':       "My snippets"
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
            return JsonResponse(status=400,
                                data={'message': 'Check fields', 'errorlist': form.errors})
    else:
        return JsonResponse(status=400, data={'message': 'Use POST'})


def show(request, snippet_id=None, fork=False):
    active_page = None
    my_snippets = None
    if request.user.is_authenticated():
        my_snippets = request.user.snippet_set.filter(public=1).order_by('name')

    try:
        snippet = Snippet.objects.get(id=snippet_id)
        mine = snippet.author == request.user
        title = "{0} by {1}".format(snippet.name, snippet.author.username if snippet.author
                                    else "Anonymous")
        if fork:
            active_page = 'create'
            title = "Fork " + title
            fork = Snippet()
            fork.name = snippet.name + "-fork"
            if request.user.is_authenticated():
                fork.author = request.user
            fork.public = 1
            fork.code = snippet.code
            fork.language = snippet.language
            snippet = fork
            mine = True
    except Snippet.DoesNotExist:
        title = "Create snippet"
        active_page = 'create'
        snippet = None
        mine = True
    return render_to_response('snippetalk/snippet.html',
                              {
                                  'snippet':     snippet,
                                  'mine':        mine,
                                  'langs':       LANG_JS,
                                  'plain_text':  PLAIN_TEXT,
                                  'title':       title,
                                  'active_page': active_page,
                                  'my_snippets': my_snippets
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
                                                          'mod_time': snippet.modified_str})
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


def comment(request):
    if request.method == 'POST':
        try:
            print(json.loads(request.POST['snippets']))
            snippet = Snippet.objects.get(id=int(request.POST['id']))
            parent = Comment.objects.get(id=int(request.POST['parent'])) if request.POST['parent'] else None
            comm = Comment()
            comm.text = wrap_links(request.POST['comment'])
            comm.author = request.user if request.user.is_authenticated() else None
            comm.to_snippet = snippet
            comm.parent = parent
            comm.save()
            for s_id in json.loads(request.POST['snippets']):
                m_snippet = Snippet.objects.get(id=int(s_id))
                comm.snippets.add(m_snippet)
                m_snippet.save()
            comm.save()
            return JsonResponse(status=200,
                                data={
                                    'parent_id': comm.parent.id if comm.parent else 0,
                                    'html': comm.render(),
                                    'comment_count': snippet.comments.count()
                                })
        except Snippet.DoesNotExist:
            return JsonResponse(status=404, data={'message': "Snippet not found"})
    else:
        return JsonResponse(status=400, data={'message': "Use POST"})


def download(request, snippet_id):
    snippet = get_object_or_404(Snippet, id=snippet_id)
    filename = snippet.get_file()
    file = open(filename)
    response = HttpResponse(file)
    file.close()
    os.remove(filename)
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    return response


def upload(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = Snippet()
            name, lang_code = parse_filename(request.FILES['file'].name)
            code = request.FILES['file'].read().decode()
            snippet.language = lang_code
            highlighted = highlight(code, snippet.get_language_display())

            return JsonResponse(status=200, data={
                'message': "ok",
                'name': name,
                'lang_code': lang_code,
                # 'lang_name': snippet.get_language_display(),
                'raw': code,
                'highlighted': highlighted
            })
        else:
            return JsonResponse(status=400, data={'message': "Bad data"})
    else:
        return JsonResponse(status=400, data={'message': "Use POST"})


def preview(request):
    if request.method == 'GET':
        try:
            if not request.GET['id']:
                return JsonResponse(status=400, data={'message': "Missing parameter"})
            snippet = Snippet.objects.get(id=request.GET['id'])
            return JsonResponse(status=200, data={'code': snippet.highlighted})
        except Snippet.DoesNotExist:
            return JsonResponse(status=404, data={'message': "Snippet not found"})
    else:
        return JsonResponse(status=400, data={'message': "Use GET"})