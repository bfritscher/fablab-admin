from django.shortcuts import render


def change_lang(request):
    return render(request, 'base/change_lang.html')