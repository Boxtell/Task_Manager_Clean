from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from .forms import *
from .models import Task, TaskList


# Pour le formulaire de recherche on abandonne les CBV
def task_list(request):
    search_form = SearchForm(request.GET or None)
    # tasks = Task.objects.filter(task_list__list_users=request.user)
    tasks = Task.objects.all()

    if search_form.is_valid():
        task_name = search_form.cleaned_data.get('task_name')
        tasks = tasks.filter(task_name__contains=task_name)

        start_date = search_form.cleaned_data.get('start_date')
        if start_date:
            tasks = tasks.filter(task_due_date__gte=start_date)

        end_date = search_form.cleaned_data.get('end_date')
        if end_date:
            tasks = tasks.filter(task_due_date__lte=end_date)

        task_status = search_form.cleaned_data.get('task_status')
        if task_status:
            tasks = tasks.filter(task_ended=task_status)

        task_scope = search_form.cleaned_data.get('task_scope')
        if task_scope is True:
            tasks = tasks.filter(task_list__list_users=request.user)

    context = {'tasks': tasks,
               'form': search_form}

    return render(request=request,
                  template_name='todolist/task_list.html',
                  context=context)


def task_manager(request, pk=None):
    if pk:
        task = Task.objects.get(pk=pk)

        form = NewTaskForm(request.POST or None,
                           instance=task)
        action = 'Update'
    else:
        form = NewTaskForm(request.POST or None)
        action = 'Create'

    if form.is_valid():
        form.save()

    return render(request=request,
                  template_name='todolist/task_form.html',
                  context={'form': form,
                           'action': action})


def delete_task(request, pk):
    Task.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('todolist:task_list'))


def display_task_detail(request, pk):
    task_to_display = Task.objects.get(pk=pk)

    context = {'task': task_to_display}

    return render(request=request,
                  template_name='todolist/task_detail.html',
                  context=context)


def go_to_description(task_id):
    return HttpResponseRedirect(reverse('todolist:display_task_detail', kwargs={'task_id': task_id}))


def go_to_list_content(task_id):
    return HttpResponseRedirect(reverse('todolist:open_list', kwargs={'task_list_id': task_id}))


@login_required
def go_to_home(request):
    return HttpResponseRedirect(reverse('todolist:list-list'))


def go_to_admin(request):
    return HttpResponseRedirect(reverse('admin'))


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = '__all__'
    success_url = reverse_lazy('todolist:list-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class TaskEditView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'todolist/task_list.html'
    context_object_name = 'tasks'


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'todolist/task_detail.html'


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'todolist/task_delete.html'


class ListListView(LoginRequiredMixin, ListView):
    model = TaskList
    template_name = 'todolist/task_list_list.html'

    def get_queryset(self):
        return TaskList.objects.filter(list_users=self.request.user)


class ListDetailView(LoginRequiredMixin, DetailView):
    model = TaskList
    template_name = 'todolist/task_list_detail.html'


class ListCreateView(LoginRequiredMixin, CreateView):
    model = TaskList
    fields = '__all__'
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('todolist:list-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class ListEditView(LoginRequiredMixin, UpdateView):
    model = TaskList
    fields = '__all__'
    template_name = 'todolist/task_form.html'
    success_url = reverse_lazy('todolist:list-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Update'
        return context


class ListDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskList
    template_name = 'todolist/task_list_delete.html'
    success_url = reverse_lazy('todolist:list-list')
