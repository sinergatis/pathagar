import os

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.auth.decorators import login_required

from pathagar.books.app_settings import BOOKS_STATICS_VIA_DJANGO

from books import views
from books import forms

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Book list:
    (r'^$', 'pathagar.books.views.home',
     {}, 'home'),
    (r'^latest/$', 'pathagar.books.views.latest',
     {}, 'latest'),
    (r'^by-title/$', 'pathagar.books.views.by_title',
     {}, 'by_title'),
    (r'^by-author/$', 'pathagar.books.views.by_author',
     {}, 'by_author'),
    (r'^tags/(?P<tag>.+)/$', 'pathagar.books.views.by_tag',
     {}, 'by_tag'),
    (r'^by-popularity/$', 'pathagar.books.views.most_downloaded',
     {}, 'most_downloaded'),

    # Tag groups:
    (r'^tags/groups.atom$', 'pathagar.books.views.tags_listgroups',
     {}, 'tags_listgroups'),

    # Book list Atom:
    (r'^catalog.atom$', 'pathagar.books.views.root',
     {'qtype': u'feed'}, 'root_feed'),
    (r'^latest.atom$', 'pathagar.books.views.latest',
     {'qtype': u'feed'}, 'latest_feed'),
    (r'^by-title.atom$', 'pathagar.books.views.by_title',
     {'qtype': u'feed'}, 'by_title_feed'),
    (r'^by-author.atom$', 'pathagar.books.views.by_author',
     {'qtype': u'feed'}, 'by_author_feed'),
    (r'^tags/(?P<tag>.+).atom$', 'pathagar.books.views.by_tag',
     {'qtype': u'feed'}, 'by_tag_feed'),
    (r'^by-popularity.atom$', 'pathagar.books.views.most_downloaded',
     {'qtype': u'feed'}, 'most_downloaded_feed'),

    # Tag groups:
    (r'^tags/groups/(?P<group_slug>[-\w]+)/$', 'pathagar.books.views.tags',
     {}, 'tag_groups'),

    (r'^tags/groups/(?P<group_slug>[-\w]+).atom$', 'pathagar.books.views.tags',
     {'qtype': u'feed'}, 'tag_groups_feed'),

    # Tag list:
    (r'^tags/$', 'pathagar.books.views.tags', {}, 'tags'),
    (r'^tags.atom$', 'pathagar.books.views.tags',
     {'qtype': u'feed'}, 'tags_feed'),

    # Add, view, edit and remove books:
    url(r'^book/add$',
        login_required(views.AddBookWizard.as_view([forms.BookUploadForm,
                                                    forms.BookMetadataForm])),
        name='book_add'),
    url(r'^book/(?P<pk>\d+)/view$',
        login_required(views.BookDetailView.as_view()),
        name='book_detail'),
    url(r'^book/(?P<pk>\d+)/edit$',
        login_required(views.BookEditView.as_view()),
        name='book_edit'),
    url(r'^book/(?P<pk>\d+)/remove$',
        login_required(views.BookDeleteView.as_view()),
        name='book_delete'),

    (r'^book/(?P<book_id>\d+)/download$',
     'pathagar.books.views.download_book'),

    # Comments
    (r'^comments/', include('django.contrib.comments.urls')),

    # Add language:
    (r'^add/(?:dc_language|language)/$', 'pathagar.books.views.add_language'),

    # Auth login and logout:
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # Admin:
    (r'^admin/', include(admin.site.urls)),
)

if BOOKS_STATICS_VIA_DJANGO:
    from django.views.static import serve

    # Serve static media:
    urlpatterns += patterns(
        '',
        url(r'^static_media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

        # Book covers:
        url(r'^covers/(?P<path>.*)$', serve,
            {'document_root': os.path.join(settings.MEDIA_ROOT, 'covers')}),
    )
