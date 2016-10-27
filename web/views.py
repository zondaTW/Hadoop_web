from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from .models import Post, UploadFile
from .forms import PostForm, UploadForm
from django.utils import timezone
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
import subprocess
# Create your views here.

def post_list(request):
    posts = Post.objects.filter(published_date__isnull=False).order_by('published_date')
    return render(request, 'web/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'web/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('web.views.post_detail', pk=post.pk)             
    else:
        form = PostForm()
    return render(request, 'web/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('web.views.post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'web/post_edit.html', {'form': form})

def upload(request):
    if request.method == 'POST':
        
        un = request.POST.get('username')
        f = request.FILES.get('uploadfile') 
        
        if not(check_shell(un) and check_shell(f)):
            return render(request, 'web/upload_result.html', {'post_string': 'FUCK YOU'})


        filename = ''.join('media/' + f.name) #存放路徑   
        with open(filename,'wb+') as keys:
            for chunk in f.chunks():  #chunks()方法將文件切成塊(<=2.5M)的迭代對象
                keys.write(chunk)
    
        # check dir is exist
        if proc_check('-d /web_upload/' + un ) == 1:
            subprocess.check_output('/opt/hadoop/bin/hadoop fs -mkdir /web_upload/' + un, shell=True)

        # check file is exist
        if proc_check('-e /web_upload/' + un + '/' + f.name) == 0:
            subprocess.check_output('/opt/hadoop/bin/hadoop fs -rm /web_upload/' + un + '/' + f.name, shell=True)    
        subprocess.check_output('/opt/hadoop/bin/hadoop fs -copyFromLocal ' + filename + ' /web_upload/' + un + '/', shell=True)
        subprocess.check_output('rm ' + filename, shell=True)
        
        #更新數據表
        uf = UploadFile(username=un, uploadfile=filename)
        return render(request, 'web/upload_result.html', {'post_string': f.name + ' Upload Successful'})
    else:
        form = UploadForm()
    return render(request, 'web/upload.html', {'form': form})

def proc_check(s):
    return int(subprocess.check_output('/opt/hadoop/bin/hadoop fs -test ' + s + '; echo $?', shell=True))


def check_shell(s):
    escape = ['`', '$', ';', '|', '&', '>', '<', '*', '!', '(', ')', '?', ' ', '+' , '/', '\\']
    for i in escape:
        if i in s:
            return False
    return True
