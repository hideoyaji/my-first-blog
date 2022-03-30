from django.shortcuts import render
from .models import Post
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect

# get_race_list用
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


# Create your views here.
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

proxies_dic = {
    'http': 'proxy.server:3128',
}

def race_list(request):
    res = requests.get('https://trailrunner.jp/taikai.html', proxies=proxies_dic)
    soup = BeautifulSoup(res.text, 'html.parser')


    # 大会情報の括りである'tr'を取得
    _races = soup.find_all('tr')

    # 大会一覧リスト
    races = []

    # 大会ごとに値を取得するためのループ
    for i, race in enumerate(_races):
        race_dic = {}
        race_data = race.find_all('td')
        race_dic['開催日'] = race_data[0].text.replace('\n', '').replace('\xa0', '').replace('_', '〜')
        _race_info = race_data[1].text.replace('\n', '').replace('\xa0', '')

        # 距離情報がある場合('【’の先にある)
        if '【' in _race_info:
            race_info = _race_info.replace('\n', '').replace('】', '').replace('HP', '').split('【')
            race_dic['大会名'] = race_info[0]
            race_dic['距離'] = race_info[1]

        # 距離情報がない場合
        else:
            race_name = _race_info.replace('\n', '')
            race_dic['大会名'] = race_info[0]
            race_dic['距離'] = '未発表'

        # URL情報の取得
        race_urls = race.find_all('a')
        if len(race_urls) == 1:
            race_dic['URL'] = race_urls[0].get('href')
        else:
            race_dic['URL'] = race_urls[1].get('href')

        # 開催日、大会名、距離を格納した辞書を大会一覧リストへ追加    
        races.append(race_dic)

    return render(request, 'blog/race_list.html', {'races': races})
