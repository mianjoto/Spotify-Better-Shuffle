from flask import redirect, url_for

def redirect_to_signin(url_for_signature: str = 'index'):
    return redirect(url_for(url_for_signature))

def redirect_to_sign_in_if_not_auth(auth_manager, cache_handler, url_for_signature: str = 'index'):
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(url_for(url_for_signature))