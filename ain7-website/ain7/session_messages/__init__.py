"""
Lightweight session-based messaging system for use until #4604 finally lands.

Time-stamp: <2008-07-19 22:44:56 carljm __init__.py>

"""
VERSION = (0, 1, 'pre')

def create_message (request, message):
    """
    Create a message in the current session.

    Return True if message was saved in session, or False if it
    couldn't be (likely because session framework is not in
    INSTALLED_APPS).

    """
    if hasattr(request, 'session'):
        try:
            request.session['messages'].append(message)
        except KeyError:
            request.session['messages'] = [message]
        return True
    return False

def get_and_delete_messages (request):
    """
    Get and delete all messages for current session.

    """
    if hasattr(request, 'session'):
        return request.session.pop('messages', [])
    return []
