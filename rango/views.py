from django.contrib.auth import authenticate, login, logout
from rango.forms import CategoryForm, PageForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
#import the Page and Categories models
from rango.models import Category, Page
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required


def index(request):
    #Query database for alist of ALL categories currently stored
    #Order the categories by the number of likes in descending order
    #Retrieve the top 5 only == or all if less than 5
    #Place the list in our context_dict dictionary that will be passed
    #onto the template engine
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict={}
    context_dict['boldmessage']='Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories']=category_list
    context_dict['pages'] = page_list

    #render the response and send it back
    return render(request, 'rango/index.html', context=context_dict)
    

def about(request):
    #context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    #Create a context dictionary to pass to the template rendering engine
    context_dict ={}

    try:
        #Can we find a categry name slug with the given name?
        category = Category.objects.get(slug=category_name_slug)
        #Retrieve all the assicated pages. Filter() returns list of page objects or empty list
        pages = Page.objects.filter(category=category)
        #Adds results list to the template context under name pages
        context_dict['pages']=pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        #This executes if unable to find the specified category 
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    #A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            #The supplied form contained errors
            #print to terminal
            print(form.errors)
    #render the form with error messages
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    #You cannot add a page to a Category that does not exist
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    context_dict = {'form':form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', context = {'user_form':user_form, 'profile_form':profile_form,'registered':registered})

def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
        # Is the account active? It could have been disabled.
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html')
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return redirect(reverse('rango:index'))