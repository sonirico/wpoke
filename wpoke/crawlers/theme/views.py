from quart import request, jsonify

from wpoke import exceptions as general_exceptions
from wpoke.middleware import captcha_required
from wpoke.utils import json_response
from wpoke.validators.url import validate_url

from .crawler import get_theme_metadata_by_style_css
from .exceptions import *


@captcha_required
async def theme_detect():
    data = await request.get_json()
    target_url = data.get('url')

    if not target_url:
        return json_response(400, message="A target URI must be supplied")

    try:
        validate_url(target_url)
    except general_exceptions.ValidationError as e:
        return json_response(400, message=e.message)

    try:
        themes_metadata = await get_theme_metadata_by_style_css(target_url)
    except general_exceptions.MalformedBodyException:
        return json_response(422, message='Target unreadable')
    except general_exceptions.TargetNotFound:
        return json_response(422, message="Target not found")
    except (general_exceptions.TargetInternalServerError,
            general_exceptions.TargetTimeout):
        return json_response(422, message="Target unavailable")
    except general_exceptions.NastyTargetException:
        return json_response(418, message="Nasty target")
    except BundledThemeException as e:
        return json_response(422, message=e.message)
    except ThemePathMissingException:
        return json_response(422, message="Maybe not a WordPress site?")

    result = {
        'target_url': target_url,
        'themes': [
            theme_metadata.deserialize()
            for theme_metadata in themes_metadata
        ]
    }

    return jsonify(result)
