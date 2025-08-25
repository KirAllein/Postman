from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Template
from .froms import TemplateForm

from .YandexGPT import generation_letter

# шаблоны писем кандидатам
@login_required
def templates(request):
    templates = Template.objects.all()
    return render(request, 'templates/templates.html', {'templates': templates})


# создание шаблона письма
@login_required
def template_create(request):
    letter = None
    title = None

    if request.method == 'POST':
        form = TemplateForm(request.POST)
        if form.is_valid():
            action = request.POST.get('action')

            if action == 'generate':
                vacancy = form.cleaned_data['vacancies'] if 'vacancies' in form.cleaned_data else None
                if vacancy:
                    if hasattr(vacancy, 'all'):
                        vacancy = vacancy.first()
                    if vacancy:
                        letter = generation_letter(vacancy.title, vacancy.description)
                        title = vacancy.title
                        print(letter)
            elif action == 'save':
                template = form.save(commit=False) # сразу не сохраняем в бд
                if letter:
                    template.content = letter
                template.save()
                form.save_m2m()  # сохраняем связи M2M
                return redirect('templates')
    else:
        form = TemplateForm()

    return render(request, 'templates/template_create.html', {'form': form, 'generated_text': letter,
                                                              'vacancy_title': title})


# редактирование шаблона письма
@login_required
def template_edit(request, pk):
    template = get_object_or_404(Template, pk=pk)

    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=template)
        if form.is_valid():
            template = form.save()
            # Сбрасываем старые связи
            template.vacancies.clear()
            # Устанавливаем новые
            for vacancy in form.cleaned_data['vacancies']:
                vacancy.templates.add(template)
            return redirect('template_detail', pk=template.pk)
    else:
        form = TemplateForm(instance=template)

    return render(request, 'templates/template_create.html', {'form': form, 'editing': True})


# информация по письму
@login_required
def template_detail(request, pk):
    template = get_object_or_404(Template, pk=pk)
    return render(request, 'templates/template_detail.html', {'template': template})


# удаление пиьсма
@login_required
def template_delete(request, pk):
    template = get_object_or_404(Template, pk=pk)
    if request.method == 'POST':
        template.delete()
        return redirect('templates')
    return render(request, 'templates/template_detail.html', {'template': template})