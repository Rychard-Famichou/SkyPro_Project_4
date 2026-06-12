from django.contrib import admin
from django.urls import path

from newsletters.views import HomePageView, NewsletterCreateView, NewsletterListView, NewsletterDetailView, \
    NewsletterUpdateView, NewsletterDeleteView, RecipientListView, RecipientCreateView, RecipientDetailView, \
    RecipientUpdateView, RecipientDeleteView, MessageCreateView, MessageListView, MessageDetailView, MessageUpdateView, \
    MessageDeleteView, NewsletterSendView

app_name = "newsletters"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', HomePageView.as_view(), name='home'),
    path('newsletter_form/', NewsletterCreateView.as_view(), name='newsletter_form'),
    path('newsletter_list/', NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletter_detail/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletter_detail/<int:pk>/edit/', NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('newsletter_detail/<int:pk>/delete/', NewsletterDeleteView.as_view(), name='newsletter_delete'),
    path('newsletter_detail/<int:pk>/send/', NewsletterSendView.as_view(), name='newsletter_send'),
    path('recipient_form/', RecipientCreateView.as_view(), name='recipient_form'),
    path('recipient_list/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient_detail/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient_detail/<int:pk>/edit/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient_detail/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),
    path('message_form/', MessageCreateView.as_view(), name='message_form'),
    path('message_list/', MessageListView.as_view(), name='message_list'),
    path('message_detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message_detail/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('message_detail/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

]