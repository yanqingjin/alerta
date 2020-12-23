import logging

from datetime import datetime
from flask import current_app
from alerta.app import alarm_model
from alerta.models.alert import Alert
from alerta.exceptions import ApiError
from . import WebhookBase

LOG = logging.getLogger('alerta.webhooks')

class CloudMonitorWebhook(WebhookBase):
    """
    AliCloud CloudMonitor webhook receiver
    See https://help.aliyun.com/document_detail/60714.html
    """

    @staticmethod
    def trigger_level_to_severity(trigger_level: str) -> str:
        if trigger_level == 'CRITICAL':
            return 'critical'
        elif trigger_level == 'WARN':
            return 'warning'
        elif trigger_level == 'INFO':
            return 'info'
        elif trigger_level == 'OK':
            return alarm_model.DEFAULT_NORMAL_SEVERITY
        else:
            return 'unknown'

    def incoming(self, path, query_string, payload):
        LOG.info('payload: {}'.format(payload))

        if payload and 'alertName' in payload:

            app = payload['instanceName'] or 'Unknown-Unknown'
            ind = app.find('-')

            project = app[:ind]
            service = [app[ind + 1:]]
            resource = service[0]

            return Alert(
                event=payload['alertName'],
                project=project,
                service=service,
                resource=resource,
                environment='HSC',
                severity=self.trigger_level_to_severity(payload['triggerLevel']),
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
                }
            )
        else:
            raise ApiError('no alerts in CloudMonitor notification payload', 400)
