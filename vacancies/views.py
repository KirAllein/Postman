from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Vacancy
from .forms import VacancyForm

import json
from django.http import JsonResponse

from .emails import send_email_to_candidate


# список вакансий
@login_required
def vacancies(request):
    vacancies = Vacancy.objects.filter(user_company=request.user.company)
    return render(request, 'vacancies/vacancies.html', {'vacancies': vacancies})


# создание новой вакансии
@login_required
def vacancy_create(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.user = request.user
            vacancy.user_company = request.user.company
            vacancy.save()
            form.save_m2m()
            return redirect('vacancies')
    else:
        form = VacancyForm()
    return render(request, 'vacancies/vacancy_create.html', {'form': form})


# подробная информация о вакансии
@login_required
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})


# редактирование вакансии
@login_required
def vacancy_edit(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.save()
            form.save_m2m()
        return redirect('vacancy_detail', pk=vacancy.pk)
    else:
        form = VacancyForm(instance=vacancy)

    return render(request, 'vacancies/vacancy_create.html', {'form': form, 'editing': True})


# удаление вакансии
@login_required
def vacancy_delete(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.method == 'POST':
        vacancy.delete()
        return redirect('vacancies')
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})


# Отправка писем кандидатам
@login_required
@require_POST
def send_vacancy_emails(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    username = request.user.username

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Некорректный JSON"},
            status=400,
            json_dumps_params={'ensure_ascii': False}
        )

    candidate_ids = data.get('candidates', [])
    template_id = data.get('template_id')

    if not candidate_ids:
        return JsonResponse({'success': False, "message": 'Ну выбери, кому ты там писать собрался'}, status=400,
                            json_dumps_params={'ensure_ascii': False})
    if not template_id:
        return JsonResponse({'success': False, "message": 'Надо выбрать письмо, которое будешь отправлять'}, status=400,
                            json_dumps_params={'ensure_ascii': False})

    template = get_object_or_404(vacancy.templates, id=template_id)
    candidates = vacancy.candidates.filter(id__in=candidate_ids)

    sent = 0
    errors = []
    for c in candidates:
        if c.email:
            # функция отправки
            if c.status == "Письмо отправлено":
                errors.append(f"{username}, хорош спамить {c.firstname} {c.surname}!! Письмо уже отправлено!!!")
            else:
                send_email_to_candidate(c, template)
                c.status = "Письмо отправлено"
                c.save(update_fields=["status"])
                sent += 1
    if errors:
        return JsonResponse(
            {"success": sent > 0, "message": "; ".join(errors)},
            json_dumps_params={'ensure_ascii': False}
        )

    return JsonResponse(
        {"success": True, "message": f"Письма отправлены {sent} кандидатам."},
        json_dumps_params={'ensure_ascii': False}
    )
