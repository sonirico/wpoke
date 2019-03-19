from wpoke.views import bp_api

from .views import theme_detect


bp_api.route('theme/detect/', methods=['POST'])(theme_detect)
