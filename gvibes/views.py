from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from .decorator import *
from django.core.exceptions import PermissionDenied
from datetime import datetime
from datetime import date

# Create your views here.


@OnlyAuth
def signin(request):
    LM = LoginForm(request.POST or None)
    if request.method == 'POST':
        if LM.is_valid():
            UserName = request.POST.get('username')
            PassWord = request.POST.get('password')
            user = authenticate(request, username=UserName, password=PassWord)

            if user is not None and user.is_cdc:
                login(request, user)
                return redirect('cdc')
            elif user is not None and user.is_teacher:
                login(request, user)
                return redirect('teacher')
            elif user is not None and user.is_student:
                login(request, user)
                return redirect('student')
            else:
                messages.error(request, 'Username or Password is incorrect')
        else:
            messages.error(request, LM.errors)
    else:
        LM = LoginForm()
    context = {'form': LM}
    return render(request, 'common/signin.html', context)


@OnlyAuth
def signup(request):
    if request.method == 'POST':
        SF = SignupForm(request.POST)
        if SF.is_valid():
            isStudent = SF.cleaned_data.get('is_student')
            isTeacher = SF.cleaned_data.get('is_teacher')
            if isStudent:
                SignUpUser = SF.save(commit=False)
                SignUpUser.is_student = True
                SignUpUser.status = True
                SignUpUser.save()
            elif isTeacher:
                SignUpUser = SF.save(commit=False)
                SignUpUser.is_teacher = True
                SignUpUser.status = False
                SignUpUser.save()
            else:
                messages.warning(request, 'Please Select Your user Type')
                return redirect('signin')
            user = SF.cleaned_data.get('username')
            messages.success(request, 'Account Created for ' + user)
            return redirect('signin')
        else:
            messages.error(request, SF.errors)
    else:
        SF = SignupForm()
    context = {'form': SF}
    return render(request, 'common/signup.html', context)


@login_required(login_url='signin')
def signout(request):
    logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def student(request):
    if not request.user.is_student:
        raise PermissionDenied
    if not request.user.status:
        return render(request, 'common/notActive.html')

    userdata = User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        UserProfileForm = SignupForm(
            request.POST, request.FILES, instance=userdata)

        if UserProfileForm.is_valid():
            student = UserProfileForm.save(commit=False)
            student.is_student = True
            student.status = True
            UserProfileForm.save()
            messages.success(request, 'Profile is Updated')
        else:
            messages.warning(request, UserProfileForm.errors)
    else:
        UserProfileForm = SignupForm(instance=userdata)
    context = {'StudentData': userdata, 'UserProfileForm': UserProfileForm}
    return render(request, 'student/StudentProfile.html', context)

@login_required(login_url='signin')
def teacher(request):
    if not request.user.is_teacher:
        raise PermissionDenied
    if not request.user.status:
        return render(request, 'common/notActive.html')

    return render(request, 'student/StudentProfile.html')

@login_required(login_url='signin')
def addpin(request):
    if not request.user.status:
        return render(request, 'common/notActive.html')

    userdata = User.objects.get(pk=request.user.id)

    try:
        pindetails = Pin.objects.all()
    except Pin.DoesNotExist:
        pindetails = None

    AllPin = []
    if pindetails is not None:
        for ND in pindetails:
            user = User.objects.get(pk=ND.owner)
            if user is not None:
                author = user.first_name + ' ' + user.last_name
                img = user.profilepic.url
            else:
                author = ""

            AllPin.append({
                "id": ND.id,
                "heading": ND.heading,
                "details": ND.details,
                'pincategory': ND.pincategory,
                'dept': ND.pincategory,
                'tag': ND.tag,
                'owner': ND.owner,
                'ownername': author,
                'ownerimg': img,
                "postedtime": ND.postedtime,
                'pin': ND.pin
            })

    if request.method == 'POST':
        PinForm = PinManagement(request.POST, request.FILES)
        if PinForm.is_valid():
            pin = PinForm.save(commit=False)
            pin.status = True
            pin.owner = request.user.id
            pin.postedtime = date.today()
            pin.save()
            messages.success(
                request, 'Your News Pin is submited and wait for CDC process')
            return redirect('allpin')
        else:
            messages.warning(request, PinForm.errors)
    else:
        PinForm = PinManagement()
    context = {'StudentData': userdata,
               'AllPin': AllPin, 'PinForm': PinForm}
    return render(request, 'pin/addpin.html', context)


@login_required(login_url='signin')
def allpin(request):
    if not request.user.status:
        return render(request, 'common/notActive.html')
    userdata = User.objects.get(pk=request.user.id)
    imgclass = ['large polaroid img1', 'polaroid img2', 'medium polaroid img4', 'polaroid img5',
                'polaroid img6', 'polaroid img7', 'medium polaroid img9', 'polaroid img10', 'polaroid img15']

    try:
        pindetails = Pin.objects.all()
    except Pin.DoesNotExist:
        pindetails = None

    pinNews = []
    if pindetails is not None:
        for ND in pindetails:
            user = User.objects.get(pk=ND.owner)
            if user is not None:
                author = user.first_name + ' ' + user.last_name
                img = user.profilepic.url
            else:
                author = ""

            pinNews.append({
                "id": ND.id,
                "heading": ND.heading,
                "details": ND.details,
                'pincategory': ND.pincategory,
                'dept': ND.pincategory,
                'tag': ND.tag,
                'owner': ND.owner,
                'ownername': author,
                'ownerimg': img,
                "postedtime": ND.postedtime,
                'pin': ND.pin
            })
    context = {'StudentData': userdata,
               'pinNews': pinNews, 'imgclass': imgclass}
    return render(request, 'pin/Allpin.html', context)


@login_required(login_url='signin')
def pindetails(request, pk):
    userdata = User.objects.get(pk=request.user.id)
    pindetails = Pin.objects.get(pk=pk)
    context = {'StudentData': userdata, 'pindetails': pindetails}
    return render(request, 'pin/pindetails.html', context)


@login_required(login_url='signin')
def editpin(request, pk):
    if not request.user.status:
        return render(request, 'common/notActive.html')

    userdata = User.objects.get(pk=request.user.id)
    pindata = Pin.objects.get(pk=pk)

    imgclass = ['large polaroid img1', 'polaroid img2', 'small polaroid img3', 'medium polaroid img4', 'polaroid img5', 'polaroid img6', 'polaroid img7', 'small polaroid img8',
                'medium polaroid img9', 'polaroid img10', 'small polaroid img11', 'small polaroid img12', 'small polaroid img13', 'small polaroid img14', 'polaroid img15']

    if request.method == 'POST':
        PinForm = PinManagement(request.POST, request.FILES, instance=pindata)
        if PinForm.is_valid():
            pin = PinForm.save(commit=False)
            pin.status = True
            pin.owner = request.user.id
            pin.postedtime = date.today()
            pin.save()
            messages.success(
                request, 'Your News Pin is Updated ')
        else:
            messages.warning(request, PinForm.errors)
    else:
        PinForm = PinManagement(instance=pindata)
    context = {'StudentData': userdata, 'PinForm': PinForm,
               'pindata': pindata, 'imgclass': imgclass}
    return render(request, 'pin/addpin.html', context)


@login_required(login_url='signin')
def deletepin(request, pk):
    if not request.user.status:
        return render(request, 'common/notActive.html')
    if request.method == 'POST':
        target_data = Pin.objects.get(pk=pk)
        target_data.delete()
        messages.success(request, 'your pin deleted')
        return redirect('allpin')

    ''' pinimage = Pin.objects.get(pk=pk)
    pinimage.delete()
    messages.success(request, 'your pin deleted')
    return redirect(request, 'allpin') '''
