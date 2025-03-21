from django.shortcuts import redirect
from .models import GroupMember


def user_belongs_to_group(view_func):
    def _wrapped_view(request, *args, **kwargs):
        group_id = kwargs.get('group_id')  # Pobieramy group_id z argumentów URL

        # Sprawdzamy, czy użytkownik należy do grupy
        try:
            group_member = GroupMember.objects.get(user=request.user, group_id=group_id)
        except GroupMember.DoesNotExist:
            # Jeśli użytkownik nie jest członkiem grupy, przekierowujemy na stronę błędu
            return redirect('error_page')  # Możesz przekierować na stronę błędu lub inną

        # Jeśli użytkownik należy do grupy, wywołaj widok
        return view_func(request, *args, **kwargs)

    return _wrapped_view