import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
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

        response = []
        for vacancy in self.object_list:
            response.append({
                "id": vacancy.id,
                "text": vacancy.text,
            })

        return JsonResponse(response, safe=False)


class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        vacancy = self.get_object()

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
            try:
                skill_obj = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return JsonResponse({"error": "Skill not found"}, status=404)
            self.object.skills.add(skill_obj)

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
