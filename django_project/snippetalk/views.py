from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from snippetalk.forms import SnippetForm
from snippetalk.models import Snippet


def recent(request):
    snippets = Snippet.objects.all().order_by('-modified')
    return render_to_response('snippetalk/list.html',
                              {
                                  'active_page': "recent",
                                  'snippets': snippets,
                                  'title': "Recent snippets"
                              },
                              RequestContext(request))


@login_required
def my(request):
    snippets = Snippet.objects.filter(author=request.user)
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
            return HttpResponseRedirect('/snippetalk/{0}/'.format(snippet.id))
    form = SnippetForm()
    return render_to_response('snippetalk/create.html',
                              {
                                  'active_page': 'create',
                                  'form': form
                              },
                              RequestContext(request))


def show(request, snippet_id):
    snippet = get_object_or_404(Snippet, id=snippet_id)
    return render_to_response('snippetalk/show.html',
                              {
                                  'snippet': snippet
                              },
                              RequestContext(request))
