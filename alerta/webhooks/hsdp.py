from typing import Any, Dict

from alerta.app import alarm_model
from alerta.models.alert import Alert
from alerta.exceptions import ApiError
from . import WebhookBase

JSON = Dict[str, Any]


def parse_hsdp(alert: JSON, group_labels: Dict[str, str], external_url: str) -> Alert:

    status = alert.get('status', 'firing')

    # Allow labels and annotations to use python string formats that refer to
    # other labels eg. runbook = 'https://internal.myorg.net/wiki/alerts/{app}/{alertname}'

    labels = {}
    for k, v in alert['labels'].items():
        try:
            labels[k] = v.format(**alert['labels'])
        except Exception:
            labels[k] = v

    annotations = {}
    for k, v in alert['annotations'].items():
        try:
            annotations[k] = v.format(**labels)
        except Exception:
            annotations[k] = v

    if status == 'firing':
        severity = labels.pop('severity', 'warning')
        if severity == 'error':
            severity = 'warning'
    elif status == 'resolved':
        severity = alarm_model.DEFAULT_NORMAL_SEVERITY
    else:
        severity = 'unknown'

    # labels
    # pop返回字典中的key对应的值并且在字典中删除这一对键值对
    resource = labels.pop('application', None) or group_labels.get('application')
    # 如果labels里面没有内容，groupLabels去找, 找不到，默认None
    event = labels.pop('event', None) or labels.pop('alertname', None) or group_labels.get('alertname')
    environment = 'HSDP'
    customer = labels.pop('customer', None)
    correlate = labels.pop('correlate').split(',') if 'correlate' in labels else None
    service = [labels.pop('application', None) or group_labels.get('application')]
    group = labels.pop('group', None) or labels.pop('organization', None) or labels.pop('job', 'HSDP')
    origin = 'hsdp/' + labels.pop('monitor', '-')
    tags = ['{}={}'.format(k, v) for k, v in labels.items()]  # any labels left over are used for tags

    try:
        timeout = int(labels.pop('timeout', 0)) or None
    except ValueError:
        timeout = None

    # annotations
    value = annotations.pop('value', None)
    summary = annotations.pop('summary', None)
    description = annotations.pop('description', None)
    text = description or summary or '{}: {} is {}'.format(severity.upper(), resource, event)

    if external_url:
        annotations['externalUrl'] = external_url  # needed as raw URL for bi-directional integration
    if 'generatorURL' in alert:
        annotations['moreInfo'] = '<a href="{}" target="_blank">HSDP Graph</a>'.format(alert['generatorURL'])

    # attributes
    attributes = {
        'startsAt': alert['startsAt'],
        'endsAt': alert['endsAt']
    }
    attributes.update(annotations)  # any annotations left over are used for attributes

    return Alert(
        resource=resource,
        event=event,
        environment=environment,
        customer=customer,
        severity=severity,
        correlate=correlate,
        service=service,
        group=group,
        value=value,
        text=text,
        attributes=attributes,
        origin=origin,
        event_type='hsdpAlert',
        timeout=timeout,
        raw_data=alert,
        tags=tags
    )


class HsdpWebhook(WebhookBase):
    """
    HSDP Log Management alert notification webhook
    """

    def incoming(self, path, query_string, payload):

        if payload and 'alerts' in payload:
            external_url = payload.get('externalURL')
            group_labels = payload.get('groupLabels')
            return [parse_hsdp(alert, group_labels, external_url) for alert in payload['alerts']]
        else:
            raise ApiError('no alerts in HSDP notification payload', 400)
