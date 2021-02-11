from django.urls import path

from viewer import views

app_name = 'viewer'

urlpatterns = [
    # Book
    path('book/list/', views.BookListView.as_view(), name='book_list'),
    path('book/add/', views.BookCreateView.as_view(), name='book_add'),
    path('book/update/<int:pk>/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/delete/<int:pk>/', views.BookDeleteView.as_view(), name='book_delete'),

    # Bookcase
    path('bookcase/list/', views.BookcaseListView.as_view(), name='bookcase_list'),
    path('bookcase/add/', views.BookcaseCreateView.as_view(), name='bookcase_add'),
    path('bookcase/update/<int:pk>/', views.BookcaseUpdateView.as_view(), name='bookcase_update'),
    path('bookcase/delete/<int:pk>/', views.BookcaseDeleteView.as_view(), name='bookcase_delete'),

    # Book author
    path('book-author/list/', views.BookAuthorListView.as_view(), name='book_author_list'),
    path('book-author/add/', views.BookAuthorCreateView.as_view(), name='book_author_add'),
    path('book-author/update/<int:pk>/', views.BookAuthorUpdateView.as_view(), name='book_author_update'),
    path('book-author/delete/<int:pk>/', views.BookAuthorDeleteView.as_view(), name='book_author_delete'),
]
