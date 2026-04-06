import json

from django.http import JsonResponse


def parse_json(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def json_error(message, status=400):
    return JsonResponse({"error": message}, status=status)
