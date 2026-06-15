from django.contrib import admin
from django.urls import path

from newsletters.views import NewsletterCreateView, NewsletterListView, NewsletterDetailView, \
    NewsletterUpdateView, NewsletterDeleteView, RecipientListView, \
    MessageCreateView, MessageListView, MessageDetailView, MessageUpdateView, \
    MessageDeleteView, NewsletterSendView, LinkCreateView, LinkUpdateView, LinkDeleteView, LinkListView, LinkDetailView, \
    RecipientDetailView, NewsletterBlockView, NewsletterUnblockView

app_name = "newsletters"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('newsletter_form/', NewsletterCreateView.as_view(), name='newsletter_form'),
    path('newsletter_list/', NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletter_detail/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletter_detail/<int:pk>/edit/', NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('newsletter_detail/<int:pk>/delete/', NewsletterDeleteView.as_view(), name='newsletter_delete'),
    path('newsletter_detail/<int:pk>/send/', NewsletterSendView.as_view(), name='newsletter_send'),
    path('newsletter_detail/<int:pk>/block/', NewsletterBlockView.as_view(), name='newsletter_block'),
    path('newsletter_detail/<int:pk>/unblock/', NewsletterUnblockView.as_view(), name='newsletter_unblock'),
    path('recipient_form/', LinkCreateView.as_view(), name='recipient_form'),
    path('recipient_list/', LinkListView.as_view(), name='recipient_list'),
    path('recipient_admin_list/', RecipientListView.as_view(), name='recipient_admin_list'),
    path('recipient_detail/<int:pk>/', LinkDetailView.as_view(), name='recipient_detail'),
    path('recipient_admin_detail/<int:pk>/', RecipientDetailView.as_view(), name='recipient_admin_detail'),
    path('recipient_detail/<int:pk>/edit/', LinkUpdateView.as_view(), name='recipient_update'),
    path('recipient_detail/<int:pk>/delete/', LinkDeleteView.as_view(), name='recipient_delete'),
    path('message_form/', MessageCreateView.as_view(), name='message_form'),
    path('message_list/', MessageListView.as_view(), name='message_list'),
    path('message_detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message_detail/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('message_detail/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

]
