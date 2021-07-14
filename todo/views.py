from django.http.response import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt 
from django.db import IntegrityError
from django.contrib.auth import authenticate, login,logout
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.


def home(request):
    return render(request,'todo/home.html')

@csrf_exempt
def usersignup(request):
    if request.method=='GET':
        return render(request,'todo/signup.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user=User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('currenttodo')
            except IntegrityError:
                return render(request,'todo/signup.html',{'form':UserCreationForm(),'error':'This name is Taken, Try user another name'})
        else:
            return render(request,'todo/signup.html',{'form':UserCreationForm(),'error':'Password did not match'})

@login_required
def currenttodo(request):
    alltodos=Todo.objects.filter(user=request.user,datecompleted__isnull=True)
    return render(request,'todo/currenttodo.html',{'todos':alltodos})

@login_required
def completedtodo(request):
    alltodos=Todo.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')
    return render(request,'todo/completedtodo.html',{'todos':alltodos})

@csrf_exempt
@login_required
def createtodo(request):
    if request.method=='GET':
        return render(request,'todo/createtodo.html',{'form':TodoForm})
    else:
        try:
            form=TodoForm(request.POST)
            newtodo=form.save(commit=False) # Database e include hobe na
            newtodo.user=request.user
            newtodo.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request,'todo/createtodo.html',{'form':TodoForm,'error':'Title is so dirty. Try again please'})
        


@login_required
def logoutuser(request):
    logout(request)
    messages.success(request,"Successfully logged out")
    return redirect('home')
    

@csrf_exempt
def loginuser(request):
    if request.method=='GET':
        return render(request,'todo/loginuser.html',{'form':AuthenticationForm()})
    else:
        user=authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'todo/loginuser.html',{'form':AuthenticationForm(),'error':'Username or password is incorrect. Please Try again'})
        else:
            login(request,user)
            return redirect('currenttodo')


@csrf_exempt
@login_required
def viewtodo(request,todo_pk):
    todoview=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method=='GET':
        form=TodoForm(instance=todoview)
        return render(request,'todo/viewtodo.html',{'todo':todoview,'form':form})
    else:
        try:
            form=TodoForm(request.POST,instance=todoview)
            form.save()
            return redirect('currenttodo')
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todoview,'form':form,'error':'Bad Data, Try again'})


@csrf_exempt
@login_required
def completetodo(request,todo_pk):
    todoview=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'POST':
        todoview.datecompleted=timezone.now()
        todoview.save()
        return redirect('currenttodo')


@csrf_exempt
@login_required
def deletetodo(request,todo_pk):
    todoview=get_object_or_404(Todo,pk=todo_pk,user=request.user)
    if request.method == 'POST':
        todoview.delete()
        return redirect('currenttodo')






