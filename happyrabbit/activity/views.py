from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View

from happyrabbit.activity.forms import CategoryCreateForm, ActivityCreateForm, RewardRuleCreateForm
from happyrabbit.activity.models import CategoryModel, ActivityModel


class CategoryCreateView(LoginRequiredMixin, View):
    template_name = 'category/create.html'

    def get(self, request):
        category_form = CategoryCreateForm()
        message = ''
        return render(request, self.template_name, context={'category_form': category_form, 'message': message})

    def post(self, request):
        category_form = CategoryCreateForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.owner = request.user
            category.save()

            return redirect('activity-view')

        message = "Invalid Data"
        return render(request, self.template_name, context={'category_form': category_form, 'message': message})


class ActivityCreateView(LoginRequiredMixin, View):
    template_name = 'activities/create.html'

    def get(self, request):
        activity_form = ActivityCreateForm()
        categories = CategoryModel.objects.filter(Q(owner__isnull=True) | Q(owner__in=[request.user])).all()
        message = ''
        return render(request, self.template_name, context={'activity_form': activity_form, 'message': message, 'categories': categories})

    def post(self, request):
        activity_form = ActivityCreateForm(request.POST)
        if activity_form.is_valid():
            activity = activity_form.save(commit=False)
            activity.owner = request.user
            activity.save()

            return redirect('activity-view')

        message = "Invalid Data"
        return render(request, self.template_name, context={'activity_form': activity_form, 'message': message})


class RewardRuleCreateView(LoginRequiredMixin, View):
    template_name = 'reward_rule/create.html'

    def get(self, request):
        reward_rule_form = RewardRuleCreateForm()
        activities = ActivityModel.objects.filter(Q(owner__isnull=True) | Q(owner__in=[request.user])).all()
        message = ''
        return render(request, self.template_name, context={'reward_rule_form': reward_rule_form, 'message': message, 'activities': activities})

    def post(self, request):
        reward_rule_form = RewardRuleCreateForm(request.POST)
        if reward_rule_form.is_valid():
            reward_rule = reward_rule_form.save(commit=False)
            reward_rule.owner = request.user
            reward_rule.save()

            return redirect('activity-view')

        message = "Invalid Data"
        return render(request, self.template_name, context={'reward_rule_form': reward_rule_form, 'message': message})


class ActivityListView(LoginRequiredMixin, View):
    template_name = 'activities/list_view.html'

    def get(self, request):
        activities = ActivityModel.objects.filter(Q(owner__isnull=True) | Q(owner__in=[request.user])).all()
        print(activities)
        return render(request, self.template_name, context={'activities': activities})