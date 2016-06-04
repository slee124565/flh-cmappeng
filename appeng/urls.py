"""appeng URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from coolmaster.views import cm_api, hc2_vd_update_simulation, bytecmd_api,temp_feedback

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^cmapi/(?P<cmd>\w+)/$', cm_api),
    url(r'^hc2/update/$', hc2_vd_update_simulation),
    url(r'^temp/feedback/$', temp_feedback),
    url(r'^bcmd/$', bytecmd_api),
]
