from uuid import uuid4
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max
from projects.forms import ProjectForm, UpdateProjectForm
from projects.models import Project
from errors.models import Error
from requests.models import Request

class IndexView(TemplateView):
    template_name = 'panel/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        return context

@login_required
def show_project(request, id_project):
    project = get_object_or_404(Project, id=id_project)
    errors = Error.objects.filter(project=project.id).values('exception', 'url').annotate(Count('url'), Max('id'))
    #errors = Error.objects.filter(project=project.id).annotate(count_exception=Count('exception'))
    requests = Request.objects.filter(project=project.id).annotate(quant=Count('date'))
    return TemplateResponse(request, 'panel/project.html', {'project': project, 'errors': errors, 'requests': requests})

@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.instance.token = str(uuid4())
            instance = form.save()
            instance.user.add(request.user)
            return HttpResponseRedirect('/panel/projects/%d' % form.instance.id)

    else:
        form = ProjectForm()

    return TemplateResponse(request, 'panel/project_form.html', {'form': form})

@login_required
def remove_project(request, id_project):
    get_object_or_404(Project, id=id_project).delete()
    return HttpResponseRedirect('/panel/')

@login_required
def change_project(request, id_project):
    project = get_object_or_404(Project, id=id_project)

    if request.method == 'POST':
        form = UpdateProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/panel/projects/%d/' % form.instance.id)
    else:
        form = UpdateProjectForm(instance=project)

    return TemplateResponse(request, 'panel/project_form.html', {'form': form})

@login_required
def show_error(request, id_project, id_error):
    error = get_object_or_404(Error, id=id_error)
    return TemplateResponse(request, 'panel/error.html', {'error': error})

@login_required
def show_similar_errors(request, id_project, id_error):
    error = get_object_or_404(Error, id=id_error)
    similar_errors = Error.objects.filter(url=error.url, exception=error.exception).exclude(id=error.id)
    return TemplateResponse(request, 'panel/similar_errors.html', {'errors': similar_errors})
