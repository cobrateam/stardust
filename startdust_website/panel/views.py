from uuid import uuid4
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from projects.forms import ProjectForm
from projects.models import Project
from errors.models import Error


class IndexView(TemplateView):
    template_name = 'panel/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        return context

def show_project(request, id_project):
    project = get_object_or_404(Project, id=id_project)

    project_content = {'name': project.name,
                       'url': project.url}

    return TemplateResponse(request, 'panel/project.html', {'project': project_content})


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


def remove_project(request, id_project):
    get_object_or_404(Project, id=id_project).delete()
    return HttpResponseRedirect('/panel/')

def change_project(request, id_project):
    project = get_object_or_404(Project, id=id_project)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/panel/projects/%d/' % form.instance.id)
    else:
        form = ProjectForm(instance=project)

    return TemplateResponse(request, 'panel/project_form.html', {'form': form})
