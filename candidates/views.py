from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CandidateForm, UploadCandidatesForm
from .models import Candidate

import openpyxl

# список всех кандидатов
@login_required
def candidates(request):
    candidates = Candidate.objects.all()
    return render(request, 'candidates/candidates.html', {'candidates': candidates})


# подробная информация о кандидате
@login_required
def candidate_detail(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    return render(request, 'candidates/candidate_detail.html', {'candidate': candidate})


# Создание карточки кандидата
@login_required
def candidate_create(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user_company = request.user.company
            candidate.save()
            # Обновим связанные вакансии вручную
            candidate.vacancies.clear()  # Убираем все старые связи
            for vacancy in form.cleaned_data['vacancies']:
                vacancy.candidates.add(candidate)
            return redirect('candidates')
    else:
        form = CandidateForm()
    return render(request, 'candidates/candidate_create.html', {'form': form})


# редактирование карточки кандидата
@login_required
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate = form.save()
            # Обновим связанные вакансии вручную
            candidate.vacancies.clear()  # Убираем все старые связи
            for vacancy in form.cleaned_data['vacancies']:
                vacancy.candidates.add(candidate)
            return redirect('candidate_detail', pk=candidate.pk)
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'candidates/candidate_create.html', {'form': form, 'editing': True})


# загрузка списка кандидатов из файла excel
@login_required
def candidates_upload(request):
    if request.method == 'POST':
        form = UploadCandidatesForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                firstname, surname, patronymic, birthday, email, phone = row[:6]

                # Не создавать, если пустой email
                if not email:
                    continue

                Candidate.objects.create(
                    firstname=firstname,
                    surname=surname,
                    patronymic=patronymic,
                    birthday=birthday,
                    email=email,
                    phone=phone
                )

            return redirect('candidates')
    else:
        form = UploadCandidatesForm()
    return render(request, 'candidates/candidates_upload.html', {'form': form})


# удаление кандидата
@login_required
def candidate_delete(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        candidate.delete()
        return redirect('candidates')
    return render(request, 'candidates/candidate_detail.html', {'candidate': candidate})
