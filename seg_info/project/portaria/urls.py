from django.urls import include, path
from portaria import views

urlpatterns = [
    path('visitantes/', include([
        path(
            '',
            views.VisitanteListView.as_view(),
            name='visitante_list'
        ),
        path(
            'novo/',
            views.VisitanteCreateView.as_view(),
            name='visitante_form'
        ),
        # path(
        #     'json/',
        #     views.autofill_campos_ocupacaoimovel,
        #     name='resposta_json'
        # ),
        path(
            '<int:pk>/',
            views.VisitanteUpdateView.as_view(),
            name='visitante_form'
        )
    ])),
]
