from typing import Any, Dict
from alerta.models.alert import Alert

from . import WebhookBase

# tmp
from flask import jsonify

JSON = Dict[str, Any]

def parse_hsdp(alert: JSON) -> Alert:

    status = alert.get('status', 'firing')

    return Alert(
        # TODO
    )

class HsdpWebhook(WebhookBase):
    """
    #hsdplog Log Management HTTP alert notifications
    """
    def incoming(self, path, query_string, payload):
        print("path=", path)
        print("query_string=", query_string)
        print("payload=", payload)
        return jsonify(
            path=path,
            resource=query_string,
            event=payload
        )