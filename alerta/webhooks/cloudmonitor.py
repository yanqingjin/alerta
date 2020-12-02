import datetime
from typing import Any, Dict

from alerta.app import alarm_model
from alerta.exceptions import ApiError
from alerta.models.alert import Alert

from . import WebhookBase

JSON = Dict[str, Any]


class CloudMonitorWebhook(WebhookBase):
    """
    AliCloud CloudMonitor webhook receiver
    See https://help.aliyun.com/document_detail/60714.html
    """

    def incoming(self, path, query_string, payload):
        pass
