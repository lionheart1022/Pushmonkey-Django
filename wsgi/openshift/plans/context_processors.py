from models import is_black_friday, is_cool_update_offer

def should_show_black_friday_banner(request):
    if is_black_friday():
        return {'is_black_friday':True}
    return {'is_black_friday': False}

def should_show_cool_update_banner(request):
    if is_cool_update_offer():
        return {'is_cool_update': True}
    return {'is_cool_update': False}

