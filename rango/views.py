from django.shortcuts import render
from django.http import HttpResponse
#import the Page and Categories models
from rango.models import Category
from rango.models import Page

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
