from datetime import datetime

from alerta.app import alarm_model
from alerta.models.alert import Alert
from alerta.exceptions import ApiError
from . import WebhookBase


class CloudMonitorWebhook(WebhookBase):
    """
    AliCloud CloudMonitor webhook receiver
    See https://help.aliyun.com/document_detail/60714.html
    """

    @staticmethod
    def trigger_level_to_severity(trigger_level: str) -> str:
        if trigger_level == 'CRITICAL':
            return 'major'
        elif trigger_level == 'WARN':
            return 'warning'
        elif trigger_level == 'INFO':
            return alarm_model.DEFAULT_NORMAL_SEVERITY
        else:
            return 'unknown'

    def incoming(self, path, query_string, payload):
        if payload and 'alertName' in payload:
            return Alert(
                resource=payload['instanceName'],
                event=payload['alertName'],
                environment='HSC',
                severity=self.trigger_level_to_severity(payload['triggerLevel']),
                service=[payload['userId']],
                group=payload['namespace'],
                value=payload['curValue'],
                origin='CloudMonitor',
                event_type='hscAlert',
                create_time=datetime.fromtimestamp(int(payload['timestamp']) / 1000),
                text='Alert created when {} {}'.format(payload['metricName'], payload['expression']),
                attributes={
                    'dimensions': payload['dimensions'],
                    'ruleId': payload['ruleId'],
                    'signature': payload['signature']
                },
                raw_data=payload
            )
        else:
            raise ApiError('no alerts in CloudMonitor notification payload', 400)
