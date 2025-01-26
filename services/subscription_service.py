import boto3

from config import AppConfig


class SubscriptionService:

    def __init__(self):
        self.sns = boto3.client('sns', AppConfig.REGION)
        self.topic_arn = AppConfig.TOPIC_ARN
        self.subscriptions_arn = self._get_subscribers()

    def _get_subscribers(self):
        response = self.sns.list_subscriptions_by_topic(TopicArn=self.topic_arn)
        subscribers = response['Subscriptions']
        return {subscriber['Endpoint']: subscriber['SubscriptionArn'] for subscriber in subscribers}

    def subscribe_email(self, email):
        subscription_arn = self._get_subscription_arn_by_email(email)
        if not subscription_arn:
            response = self.sns.subscribe(
                TopicArn=self.topic_arn,
                Protocol='email',
                Endpoint=email
            )
            self.subscriptions_arn[email] = response['SubscriptionArn']
            return 'Subscription confirmation sent'
        return 'The e-mail is already subscribed'

    def unsubscribe_email(self, email):
        subscription_arn = self._get_subscription_arn_by_email(email)
        if subscription_arn:
            self.sns.unsubscribe(SubscriptionArn=subscription_arn)
            return 'The e-mail is now unsubscribed'
        return 'The e-mail is not subscribed'

    def _get_subscription_arn_by_email(self, email):
        next_token = None

        while True:
            if next_token:
                response = self.sns.list_subscriptions_by_topic(TopicArn=self.topic_arn, NextToken=next_token)
            else:
                response = self.sns.list_subscriptions_by_topic(TopicArn=self.topic_arn)

            subscriptions = response['Subscriptions']

            for subscription in subscriptions:
                if subscription['Endpoint'] == email:
                    subscription_arn = subscription['SubscriptionArn']
                    if subscription_arn.startswith('arn'):
                        return subscription_arn
                    return None

            next_token = response.get('NextToken')
            if not next_token:
                break

        return None
