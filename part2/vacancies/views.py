import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, EmptyResultSet
from django.db.models import Count, Avg
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from vacancies.models import Vacancy, Skill


class VacancyListView(ListView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        search_text = request.GET.get("text", None)
        if search_text:
            self.object_list = self.object_list.filter(text=search_text)

        self.object_list = self.object_list.select_related('user').prefetch_related('skills')

        total_vacancies = self.object_list.count()
        # self.object_list = self.object_list.order_by('name')

        page = int(request.GET.get("page", 0))
        offset = page * settings.TOTAL_ON_PAGE
        if offset > total_vacancies:
            self.object_list = []
        elif offset:
            self.object_list = self.object_list[offset:settings.TOTAL_ON_PAGE]
        else:
            self.object_list = self.object_list[:settings.TOTAL_ON_PAGE]

        vacancies = []
        for vacancy in self.object_list:
            vacancies.append({
                "id": vacancy.id,
                "name": vacancy.name,
                "text": vacancy.text,
                "username": vacancy.user.username,
                "skills": list(map(str, vacancy.skills.all())),
            })

        response = {
            "items": vacancies,
            "total": total_vacancies,
            "per_page": settings.TOTAL_ON_PAGE,
        }
        return JsonResponse(response, safe=False)


class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        try:
            vacancy = self.get_object()
        except Vacancy.DoesNotExist:
            return JsonResponse({"error": "Not found"}, status=404)

        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
            "user_id": vacancy.user_id,
            "slug": vacancy.slug,
            "status": vacancy.status,
            "skills": list(vacancy.skills.all().values_list("name", flat=True)),
            "created": vacancy.created,
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyCreateView(CreateView):
    model = Vacancy
    fields = ["user", "slug", "text", "status", "created", "skills"]

    def post(self, request, *args, **kwargs):
        vacancy_data = json.loads(request.body)

        vacancy = Vacancy()
        vacancy.user_id = vacancy_data["user_id"]
        vacancy.slug = vacancy_data["slug"]
        vacancy.text = vacancy_data["text"]
        vacancy.status = vacancy_data["status"]

        for skill in vacancy_data["skills"]:
            skill_obj, _ = Skill.objects.get_or_create(name=skill)
            self.object.skills.add(skill_obj)

        try:
            vacancy.full_clean()
        except ValidationError as e:
            return JsonResponse(e.message_dict, status=422)

        vacancy.save()
        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyUpdateView(UpdateView):
    model = Vacancy
    fields = ["slug", "text", "status", "skills"]

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        vacancy_data = json.loads(request.body)
        self.object.slug = vacancy_data["slug"]
        self.object.text = vacancy_data["text"]
        self.object.status = vacancy_data["status"]

        for skill in vacancy_data["skills"]:
            skill_obj, _ = Skill.objects.get_or_create(name=skill)
            self.object.skills.add(skill_obj)

        try:
            self.object.full_clean()
        except ValidationError as e:
            return JsonResponse(e.message_dict, status=422)

        self.object.save()
        return JsonResponse({
            "id": self.object.id,
            "user_id": self.object.user_id,
            "slug": self.object.slug,
            "text": self.object.text,
            "status": self.object.status,
            "skills": list(self.object.skills.all().values_list("name", flat=True)),
            "created": self.object.created,
        })


@method_decorator(csrf_exempt, name='dispatch')
class VacancyDeleteView(DeleteView):
    model = Vacancy
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


class UserVacancyDetailView(View):
    def get(self, request):
        total_users = User.objects.count()
        users_qs = User.objects.annotate(vacancies=Count('vacancy'))

        page = int(request.GET.get("page", 0))
        offset = page * settings.TOTAL_ON_PAGE
        if offset > total_users:
            users_qs = []
        elif offset:
            users_qs = users_qs[offset:settings.TOTAL_ON_PAGE]
        else:
            users_qs = users_qs[:settings.TOTAL_ON_PAGE]

        users = []
        for user in users_qs:
            users.append({
                "id": user.id,
                "name": user.username,
                "vacancies": user.vacancies,
            })

        response = {
            "items": users,
            "avg": users_qs.aggregate(Avg('vacancies')),
            "total": total_users,
            "per_page": settings.TOTAL_ON_PAGE,
        }
        return JsonResponse(response, safe=False)
