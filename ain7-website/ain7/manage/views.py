# -*- coding: utf-8
#
# manage/views.py
#
#   Copyright (C) 2007-2008 AIn7
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission, User
from django.core.paginator import ObjectPaginator, InvalidPage
from django import newforms as forms
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _

from ain7.utils import ain7_render_to_response, form_callback
from ain7.decorators import confirmation_required
from ain7.annuaire.models import Person, UserContribution
from ain7.emploi.models import Company, CompanyField, OrganizationProposal
from ain7.emploi.models import OfficeProposal
from ain7.emploi.forms import *
from ain7.manage.models import *
from ain7.emploi.views import OrganizationForm, OfficeForm

from ain7.widgets import DateTimeWidget

from ain7.fields import AutoCompleteField

class SearchPersonForm(forms.Form):
    last_name = forms.CharField(label=_('Last name'), max_length=50, required=False)
    first_name = forms.CharField(label=_('First name'), max_length=50, required=False)

class SearchGroupForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=50, required=False)

class SearchCompanyForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=50, required=False)
    location = forms.CharField(label=_('Location'), max_length=50, required=False)
    activity = forms.CharField(label=_('Activity'), max_length=50, required=False)

class SearchContributionForm(forms.Form):
    user = forms.CharField(label=_('User'), max_length=50, required=False)
    type = forms.CharField(label=_('Type'), max_length=50, required=False)

class PermGroupForm(forms.Form):
    perm = forms.CharField(label=_('Permission'), max_length=50, required=True)

class MemberGroupForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=100, required=True, widget=AutoCompleteField(url='/ajax/person/'))

class NewPersonForm(forms.Form):
    first_name = forms.CharField(label=_('First name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size':50}))
    last_name = forms.CharField(label=_('Last name'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    mail = forms.CharField(label=_('Mail'),max_length=50, required=True, widget=forms.TextInput(attrs={'size': 50}))
    nationality = forms.IntegerField(label=_('Nationality'), required=False, widget=AutoCompleteField(url='/ajax/nationality/'))
    birth_date = forms.DateTimeField(label=_('Date of birth'), required=False, widget=DateTimeWidget)
    sex = forms.IntegerField(label=_('Sex'), required=False,  widget=forms.Select(choices=Person.SEX))

class NotificationForm(forms.Form):
    title = forms.CharField(label=_('title'), max_length=50, required=True)
    details = forms.CharField(label=_('details'), required=True, widget=forms.widgets.Textarea(attrs={'rows':15, 'cols':90}))

@login_required
def index(request):
    return ain7_render_to_response(request, 'manage/default.html',
        {'notifications': Notification.objects.all()})

@login_required
def users_search(request):

    form = SearchPersonForm()
    nb_results_by_page = 25
    persons = False
    paginator = ObjectPaginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchPersonForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'last_name__contains':form.cleaned_data['last_name'].encode('utf8'),\
                      'first_name__contains':form.cleaned_data['first_name'].encode('utf8')}

            persons = Person.objects.filter(**criteria)
            paginator = ObjectPaginator(persons, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                persons = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/users_search.html',
                            {'form': form, 'persons': persons,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                             'has_next': paginator.has_next_page(page - 1),
                             'has_previous': paginator.has_previous_page(page - 1),
                             'current_page': page,
                             'next_page': page + 1,
                             'previous_page': page - 1,
                             'pages': paginator.pages,
                             'first_result': (page - 1) * nb_results_by_page +1,
                             'last_result': min((page) * nb_results_by_page, paginator.hits),
                             'hits' : paginator.hits,})

@login_required
def user_details(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    return ain7_render_to_response(request, 'manage/user_details.html', {'this_user': u})

@login_required
def user_register(request):

    form = NewPersonForm()

    if request.method == 'POST':
        form = NewPersonForm(request.POST)
        if form.is_valid():
            login = (form.cleaned_data['first_name'][0]+form.cleaned_data['last_name']).lower()
            mail = form.cleaned_data['mail']
            new_user = User.objects.create_user(login, mail, 'password')
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()

            new_person = Person()
            new_person.user = new_user
            new_person.first_name = form.cleaned_data['first_name']
            new_person.last_name = form.cleaned_data['last_name']
            new_person.complete_name = new_person.first_name+' '+new_person.last_name
            new_person.sex = form.cleaned_data['sex']
            new_person.birth_date = datetime.date(1978,11,18)
            new_person.country = Country.objects.get(id=form.cleaned_data['nationality'])
            new_person.save()

            new_couriel = Email()
            new_couriel.person = new_person
            new_couriel.email = form.cleaned_data['mail']
            new_couriel.preferred_email = True
            new_couriel.save()

            request.user.message_set.create(message=_("New user successfully created"))
            return HttpResponseRedirect('/manage/users/%s/edit' % (new_person.user.id))
        else:
            request.user.message_set.create(message=_("Something was wrong in the form you filled. No modification done."))

    back = request.META.get('HTTP_REFERER', '/')
    return ain7_render_to_response(request, 'manage/edit_form.html', {'action_title': 'Register new user', 'back': back, 'form': form})

@login_required
def companies_search(request):

    form = SearchCompanyForm()
    nb_results_by_page = 25
    companies = False
    paginator = ObjectPaginator(Company.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchCompanyForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'name__contains':form.cleaned_data['name'].encode('utf8'),
                      'is_a_proposal': False} # ,\
                      #'location__contains':form.cleaned_data['location'].encode('utf8')}

            companies = Company.objects.filter(**criteria)
            paginator = ObjectPaginator(companies, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                companies = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/companies_search.html',
        {'form': form, 'companies': companies,
         'nb_org': Company.objects.valid_organizations().count(),
         'nb_offices': Office.objects.valid_offices().count(),
         'paginator': paginator, 'is_paginated': paginator.pages > 1,
         'has_next': paginator.has_next_page(page - 1),
         'has_previous': paginator.has_previous_page(page - 1),
         'current_page': page, 'pages': paginator.pages,
         'next_page': page + 1, 'previous_page': page - 1,
         'first_result': (page - 1) * nb_results_by_page +1,
         'last_result': min((page) * nb_results_by_page, paginator.hits),
         'hits' : paginator.hits,})

@login_required
def company_edit(request, company_id=None):

    company = None
    if company_id:
        company = get_object_or_404(Company, pk=company_id)
        form = OrganizationForm(
            {'name': company.name, 'size': company.size,
             'field': company.field,
             'short_description': company.short_description,
             'long_description': company.long_description })
        action_title = _('Edit a company')
    else:
        form = OrganizationForm()
        action_title = _('Register a company')

    if request.method == 'POST':
        form = OrganizationForm(request.POST.copy())
        if form.is_valid():
            org = form.save(is_a_proposal=False, organization=company)
            if company:
                msg = _('Company successfully modified')
            else:
                msg = _('Company successfully created')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect('/manage/companies/%s/' % org.id)
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No company registered.')+str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/company_edit.html',
        {'action_title': action_title,
         'form': form, 'back': back})


@login_required
def company_details(request, company_id):
    c = get_object_or_404(Company, pk=company_id)
    return ain7_render_to_response(request, 'manage/company_details.html', {'company': c})


@confirmation_required(
    lambda user_id=None,
    company_id=None: str(get_object_or_404(Company, pk=company_id)),
    'manage/base.html',
    _('Do you REALLY want to delete this company'))
def company_delete(request, company_id):

    company = get_object_or_404(Company, pk=company_id)
    company.delete()
    request.user.message_set.create(
        message=_('Organization successfully removed'))
    return HttpResponseRedirect('/manage/')


@login_required
def organization_merge(request, organization_id=None):

    organization = get_object_or_404(Company, pk=organization_id)

    # comme on ne peut définir le queryset qu'à la déclaration du champ,
    # je dois créer le formulaire ici
    class OrganizationListForm(forms.Form):        
        org = forms.ModelChoiceField(
            label=_('organization'), required=True,
            queryset=Company.objects.valid_organizations().exclude(id=organization_id))

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        f = OrganizationListForm()
        return ain7_render_to_response(
            request, 'manage/organization_merge.html',
            {'form': f, 'organization': organization})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OrganizationListForm(request.POST.copy())
        if f.is_valid():
            organization2 = f.cleaned_data['org']
            return HttpResponseRedirect('/manage/companies/%s/merge/%s/' %
                (organization2.id, organization_id))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.'))
            return HttpResponseRedirect('/manage/companies/%s/merge/' %
                organization_id)
        

@confirmation_required(
    lambda user_id=None, org1_id=None, org2_id=None:
    str(get_object_or_404(Company, pk=org2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Company, pk=org1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def organization_do_merge(request, org1_id, org2_id):

    org1 = get_object_or_404(Company, pk=org1_id)
    org2 = get_object_or_404(Company, pk=org2_id)
    org1.merge(org2)
    request.user.message_set.create(
        message=_('Organizations successfully merged'))
    return HttpResponseRedirect('/manage/companies/%s/' % org1_id)

@login_required
def organization_register_proposal(request, proposal_id=None):

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OrganizationProposal, pk=proposal_id)
    form = OrganizationForm(
        {'name': proposal.modified.name,
         'size': proposal.modified.size,
         'field': str(proposal.modified.field),
         'short_description': proposal.modified.short_description, 
         'long_description': proposal.modified.long_description })

    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            company = form.save(is_a_proposal=False)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(
                organization_proposal=proposal )
            notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Organization successfully created'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No company registered.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Proposal for adding an organization'),
         'form': form, 'back': back})

@login_required
def office_edit(request, office_id=None, organization_id=None):

    office = None
    if office_id:
        office = get_object_or_404(Office, pk=office_id)
        form = OfficeForm(
            {'company': office.company.id, 'name': office.name,
            'line1': office.line1, 'line2': office.line2,
            'zip_code': office.zip_code, 'city': office.city,
            'country': office.country.id, 'phone_number': office.phone_number,
            'web_site': office.web_site})
        action_title = _('Edit an office')

    else:
        form = OfficeForm({'company': organization_id})
        action_title = _('Register an office')

    if request.method == 'POST':
        form = OfficeForm(request.POST.copy())
        if form.is_valid():
            office = form.save(is_a_proposal=False, office=office)
            if office_id:
                msg = _('Office successfully modified')
            else:
                msg = _('Office successfully created')
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect('/manage/offices/%s/' % office.id)
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled.'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/company_edit.html',
        {'action_title': action_title, 'form': form, 'back': back})


@login_required
def office_details(request, office_id):
    office = get_object_or_404(Office, pk=office_id)
    return ain7_render_to_response(request, 'manage/office_details.html',
        {'office': office})


@confirmation_required(
    lambda user_id=None,
    office_id=None: str(get_object_or_404(Office, pk=office_id)),
    'manage/base.html',
    _('Do you REALLY want to delete this office'))
def office_delete(request, office_id):

    office = get_object_or_404(Office, pk=office_id)
    company_id = office.company.id
    office.delete()
    request.user.message_set.create(
        message=_('Office successfully removed'))
    return HttpResponseRedirect('/manage/companies/%s/' % company_id)


@login_required
def office_merge(request, office_id=None):

    office = get_object_or_404(Office, pk=office_id)

    # comme on ne peut définir le queryset qu'à la déclaration du champ,
    # je dois créer le formulaire ici
    class OfficeListForm(forms.Form):        
        bureau = forms.ModelChoiceField(
            label=_('office'), required=True,
            queryset=Office.objects.valid_offices().exclude(id=office_id))

    # 1er passage : on demande la saisie d'une deuxième organisation
    if request.method == 'GET':
        f = OfficeListForm()
        return ain7_render_to_response(
            request, 'manage/office_merge.html', {'form':f, 'office':office})

    # 2e passage : sauvegarde, notification et redirection
    if request.method == 'POST':
        f = OfficeListForm(request.POST.copy())
        if f.is_valid():
            office2 = f.cleaned_data['bureau']
            return HttpResponseRedirect('/manage/offices/%s/merge/%s/' %
                (office2.id, office_id))
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.')+str(f.errors))
            return HttpResponseRedirect('/manage/offices/%s/merge/' %
                office_id)
        

@confirmation_required(
    lambda user_id=None, office1_id=None, office2_id=None:
    str(get_object_or_404(Office, pk=office2_id)) + _(' replaced by ') + \
    str(get_object_or_404(Office, pk=office1_id)),
    'manage/base.html',
    _('Do you REALLY want to have'))
def office_do_merge(request, office1_id, office2_id):

    office1 = get_object_or_404(Office, pk=office1_id)
    office2 = get_object_or_404(Office, pk=office2_id)
    office1.merge(office2)
    request.user.message_set.create(message=_('Offices successfully merged'))
    return HttpResponseRedirect('/manage/offices/%s/' % office1_id)


@login_required
def office_register_proposal(request, proposal_id=None):

    if not proposal_id:
        return HttpResponseRedirect('/manage/')
    
    proposal = get_object_or_404(OfficeProposal, pk=proposal_id)
    form = OfficeForm({
        'company'     : proposal.modified.company.id,
        'name'        : proposal.modified.name,
        'line1'       : proposal.modified.line1,
        'line2'       : proposal.modified.line2,
        'zip_code'    : proposal.modified.zip_code,
        'city'        : proposal.modified.city,
        'country'     : proposal.modified.country.id,
        'phone_number': proposal.modified.phone_number,
        'web_site'    : proposal.modified.web_site,
        'is_valid'    : proposal.modified.is_valid
        })

    if request.method == 'POST':
        form = OfficeForm(request.POST)
        if form.is_valid():
            office = form.save(is_a_proposal=False)
            # on supprime la notification et la proposition
            notification = Notification.objects.get(office_proposal=proposal)
            notification.delete()
            proposal.delete()
            request.user.message_set.create(message=_('Office successfully created'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(message=_('Something was wrong in the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/proposal_register.html',
        {'action_title': _('Proposal for adding an office'),
         'form': form, 'back': back})

@login_required
def groups_search(request):

    form = SearchGroupForm()
    nb_results_by_page = 25
    groups = False
    paginator = ObjectPaginator(Group.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchGroupForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            criteria={'name__contains':form.cleaned_data['name'].encode('utf8')}

            groups = Group.objects.filter(**criteria)
            paginator = ObjectPaginator(groups, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                groups = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/groups_search.html',
                            {'form': form, 'groups': groups,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                    'has_next': paginator.has_next_page(page - 1),
                    'has_previous': paginator.has_previous_page(page - 1),
                    'current_page': page,
                    'next_page': page + 1,
                    'previous_page': page - 1,
                    'pages': paginator.pages,
                    'first_result': (page - 1) * nb_results_by_page +1,
                    'last_result': min((page) * nb_results_by_page, paginator.hits),
                    'hits' : paginator.hits,})

@login_required
def group_details(request, group_id):
    g = get_object_or_404(Group, pk=group_id)
    return ain7_render_to_response(request, 'manage/group_details.html', {'group': g})

@login_required
def perm_add(request, group_id):
    g = get_object_or_404(Group, pk=group_id)

    form = PermGroupForm()

    if request.method == 'POST':
        form = PermGroupForm(request.POST)
        if form.is_valid():
            p = Permission.objects.filter(name=form.cleaned_data['perm'])[0]
            g.permissions.add(p)
            request.user.message_set.create(message=_('Permission added to group'))
            return HttpResponseRedirect('/manage/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('Permission is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/groups_perm_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def perm_delete(request, group_id, perm_id):
    group = get_object_or_404(Group, pk=group_id)
    perm = get_object_or_404(Permission, pk=perm_id)

    group.permissions.remove(perm)

    request.user.message_set.create(message=_('Permission removed from group'))

    return HttpResponseRedirect('/manage/groups/%s/' % group_id)

@login_required
def member_add(request, group_id):

    g = get_object_or_404(Group, pk=group_id)

    form = MemberGroupForm()

    if request.method == 'POST':
        form = MemberGroupForm(request.POST)
        if form.is_valid():
            u = User.objects.get(id=form.cleaned_data['username'])
            u.groups.add(g)
            request.user.message_set.create(message=_('User added to group'))
            return HttpResponseRedirect('/manage/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('User is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/groups_user_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def member_delete(request, group_id, member_id):
    group = get_object_or_404(Group, pk=group_id)
    member = get_object_or_404(User, pk=member_id)

    member.groups.remove(group)

    request.user.message_set.create(message=_('Member removed from group'))

    return HttpResponseRedirect('/manage/groups/%s/' % group_id)

@login_required
def permissions(request):

    nb_results_by_page = 25

    permissions = Permission.objects.all()
    paginator = ObjectPaginator(Permission.objects.all(), nb_results_by_page)

    try:
        page = int(request.GET.get('page', '1'))
        permissions = paginator.get_page(page - 1)

    except InvalidPage:
        raise http.Http404

    return ain7_render_to_response(request, 'manage/permissions.html', {'permissions': permissions, 'paginator': paginator, 'is_paginated': paginator.pages > 1,
            'has_next': paginator.has_next_page(page - 1),
            'has_previous': paginator.has_previous_page(page - 1),
            'current_page': page,
            'next_page': page + 1,
            'previous_page': page - 1,
            'pages': paginator.pages,
            'first_result': (page - 1) * nb_results_by_page +1,
            'last_result': min((page) * nb_results_by_page, paginator.hits),
            'hits' : paginator.hits,})

@login_required
def permission_details(request, perm_id):

    permission = get_object_or_404(Permission, pk=perm_id)

    return ain7_render_to_response(request, 'manage/permission_details.html', {'permission': permission})

@login_required
def contributions(request):

    form = SearchContributionForm()
    nb_results_by_page = 25
    contributions = False
    paginator = ObjectPaginator(UserContribution.objects.none(),nb_results_by_page)
    page = 1

    if request.method == 'POST':
        form = SearchContributionForm(request.POST)
        if form.is_valid():

            # criteres sur le nom et prenom
            #criteria={'user__contains':form.cleaned_data['user'].encode('utf8')}
            criteria={}

            contributions = UserContribution.objects.filter(**criteria)
            paginator = ObjectPaginator(contributions, nb_results_by_page)

            try:
                page = int(request.GET.get('page', '1'))
                contributions = paginator.get_page(page - 1)

            except InvalidPage:
                raise http.Http404

    return ain7_render_to_response(request, 'manage/contributions.html',
                            {'form': form, 'contributions': contributions,'paginator': paginator, 'is_paginated': paginator.pages > 1,
                    'has_next': paginator.has_next_page(page - 1),
                    'has_previous': paginator.has_previous_page(page - 1),
                    'current_page': page,
                    'next_page': page + 1,
                    'previous_page': page - 1,
                    'pages': paginator.pages,
                    'first_result': (page - 1) * nb_results_by_page +1,
                    'last_result': min((page) * nb_results_by_page, paginator.hits),
                    'hits' : paginator.hits,})

@login_required
def perm_add(request, group_id):
    g = get_object_or_404(Group, pk=group_id)

    form = PermGroupForm()

    if request.method == 'POST':
        form = PermGroupForm(request.POST)
        if form.is_valid():
            p = Permission.objects.filter(name=form.cleaned_data['perm'])[0]
            g.permissions.add(p)
            request.user.message_set.create(message=_('Permission added to group'))
            return HttpResponseRedirect('/manage/groups/%s/' % group_id)
        else:
            request.user.message_set.create(message=_('Permission is not correct'))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request, 'manage/groups_perm_add.html',
                            {'form': form, 'group': g, 'back': back})

@login_required
def notification_add(request):

    form = NotificationForm()

    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notif = Notification()
            notif.title = form.cleaned_data['title']
            notif.details = form.cleaned_data['details']
            notif.save()
            request.user.message_set.create(message=_('Notification successfully created'))
            return HttpResponseRedirect('/manage/')
        else:
            request.user.message_set.create(
                message=_('Something was wrong in the form you filled. No modification done.') + str(form.errors))

    back = request.META.get('HTTP_REFERER', '/')

    return ain7_render_to_response(request,
        'manage/notification.html',
        {'action_title': _('Add a new notification'),
         'form': form, 'back': back})

@login_required
def notification_edit(request, notif_id):

    notif = get_object_or_404(Notification, pk=notif_id)
    form = NotificationForm(
        {'title':notif.title, 'details':notif.details})

    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notif.title  = form.cleaned_data['title']
            notif.details= form.cleaned_data['details']
            notif.save()
            request.user.message_set.create(
                message=_("Modifications have been successfully saved."))
        else:
            request.user.message_set.create(
                message=_("Something was wrong in the form you filled. No modification done.") + str(form.errors))
        return HttpResponseRedirect('/manage/')
    return ain7_render_to_response(
        request, 'manage/notification.html',
        {'form': form,
         'action_title': _("Modification of the notification")})

@confirmation_required(
    lambda user_id=None,
    notif_id=None: str(get_object_or_404(Notification, pk=notif_id)),
    'manage/base.html',
    _('Do you REALLY want to delete the notification'))
def notification_delete(request, notif_id):

    notif = get_object_or_404(Notification, pk=notif_id)
    proposal = None
    if notif.organization_proposal:
        proposal = notif.organization_proposal
    if notif.office_proposal:
        proposal = notif.office_proposal
    if proposal:
        proposal.delete()
    notif.delete()
    request.user.message_set.create(
        message=_("The notification has been successfully removed."))
    return HttpResponseRedirect('/manage/')
