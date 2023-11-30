from klaviyo_api import KlaviyoAPI
import os
from datetime import datetime

klaviyo = KlaviyoAPI("pk_caa33f13dd50eef23c12183244201ea731", max_delay=60, max_retries=3, test_host=None)

USE_SMART_SENDING = "FALSE"
SEND_TIME = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S')

ACCOUNT_DATA = {
    "LIST_ID": "Uj7ibu",
    "TEMPLATE_ID": "[TEMPLATE_ID]",
    "API_KEY": klaviyo,
    "SUBJECT": "ON THE RECORD: your monthly recap",
    "PREVIEW": "A look at everything you might have missed this month",
    "FROM": "hello@e.uk.yourdomain.com",
    "FROM_LABEL": "Your Domain",
    "SEND_TIME": SEND_TIME
}

def create_campaign(account_data):

    create_campaign_data = {
        "type": "campaign",
        "attributes": {
            "name": f"DAILY NEWS DIGEST",
            "channel": "email",
            "audiences": {
                "included": [account_data.get('LIST_ID')],
            },
            "send_strategy": {
                "method": "static",
                "options_static": {
                    "datetime" : account_data.get('SEND_TIME')
                }
            },
            "send_options": {"use_smart_sending": USE_SMART_SENDING},
        },
    }
    new_campaign = klaviyo.Campaigns.create_campaign({"data": create_campaign_data})
    campaign_id = new_campaign["data"]["id"]
    message_id = new_campaign["data"]["attributes"]["message"]
    create_campaign_message_assign_template_data = {
        "type": "campaign-message",
        "attributes": {
            "id": message_id,
            "template_id": account_data.get('S2pjUD'),
        },
    }

    update_campaign_message_data = {
        "type": "campaign-message",
        "id": message_id,
        "attributes": {
            "content": {
                "subject": account_data.get('SUBJECT'),
                "preview_text": account_data.get('PREVIEW'),
                "from_email": account_data.get('FROM'),
                "from_label": account_data.get('FROM_LABEL'),
            }
        },
    }
    klaviyo.Campaigns.update_campaign_message(
        message_id, {"data": update_campaign_message_data}
    )

    create_campaign_send_job_data = {
        "type": "campaign-send-job",
        "attributes": {
            "id": campaign_id,
        },
    }
    klaviyo.Campaigns.create_campaign_send_job({"data": create_campaign_send_job_data})


    return 


def main():
    create_campaign(ACCOUNT_DATA)

if __name__ == "__main__":
    main()