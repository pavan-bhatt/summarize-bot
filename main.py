import requests
import openai
#from openai import OpenAI
import os
from datetime import datetime
from bs4 import BeautifulSoup
import json
from klaviyo_api import KlaviyoAPI

#REMOVE AFTER - store as env var
klaviyo = KlaviyoAPI("pk_caa33f13dd50eef23c12183244201ea731", max_delay=60, max_retries=3, test_host=None)


KLAVIYO_HEADERS = {
    "accept": "application/json",
    "revision": "2023-10-15",
    "content-type": "application/json",
    "Authorization": "Klaviyo-API-Key pk_caa33f13dd50eef23c12183244201ea731"
}

USE_SMART_SENDING = "FALSE"
SEND_TIME = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S')

ACCOUNT_DATA = {
    "LIST_ID": "Uj7ibu",
    "TEMPLATE_ID": "S2pjUD",
    "API_KEY": klaviyo,
    "SUBJECT": "ON THE RECORD: your monthly recap",
    "PREVIEW": "A look at everything you might have missed this month",
    "FROM": "hello@e.uk.yourdomain.com",
    "FROM_LABEL": "Your Domain",
    "SEND_TIME": SEND_TIME
}


#REMOVE AFTER - store as env var
openai.api_key = "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"
#client = OpenAI(api_key=os.environ.get("ENV_NAME"))

current_date_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%S')

news_api_url = f"https://agriland.ie/wp-json/wp/v2/posts?orderby=date&order=asc&after={current_date_time}"
request = requests.get(news_api_url)
news_data = request.json()

#We can make a 2nd api call here to retrive endpoint where images are stored

#Cleaning our Summary as inital payload contains some garbage
def clean_html_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    cleaned_text = soup.get_text(separator=' ')
    return cleaned_text.replace('\n', ' ').strip()

#GPT magic below 
#Prompt - Instruction to GPT
#Engine - version of GPT to parse our prompt
#Temp - Accuracy of response inline with prompt (variance measure)
#Tokens - Something about words, spaces and punctuation GPT responds with 
def generate_summary(api_key, data):
    openai.api_key = api_key
    # Prompt below - can adjust depending on output
    prompt = f"Provide a 50-60 word teaser style summary of {data['content']} news article, highlighting all important information in a clear short paragraph with correct punctuation. \n\n"
    response = openai.Completion.create(
        engine="text-davinci-003",
        temperature=0.2,
        #frequency_penalty=0.8,
        #presence_penalty=0.3,
        prompt=prompt,
        max_tokens=200  # Adjust as needed
    )
    #global summary
    summary = response.choices[0].text.strip()
    return {
        'title': data['title'],
        'link': data['link'],
        'summary': summary
    }

#HTML Formatter - just takes our data and adds some HTML tags around it. Returns out a nice dictionary to use when building a template
def format_to_html(raw_data):
    html_data = []

    for entry in raw_data:
        title = entry['title']
        link = entry['link']
        summary = entry['summary']

        # Creating HTML formatting for each news article entry
        html = {
            'title': f"<p><h2>{title}</h2> </p>\n",
            'summary': f"<p>Summary: {summary}</p>\n",
            'link': f"<a href='{link}'>Read more</a>\n"
        }
        

        # Concatenating the HTML of each entry
        html_data.append(html)

    return html_data

TEMPLATE_HEADER_STYLE = """<head>
    <title>      
    </title>
<!--[if !mso]><!-->
    <meta content="IE=edge" http-equiv="X-UA-Compatible"/>
<!--<![endif]-->
    <meta content="width=device-width, initial-scale=1" name="viewport"/>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:AllowPNG/>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<!--[if lte mso 11]>
<style type="text/css" data-inliner="ignore">
.mj-outlook-group-fix { width:100% !important; }
</style>
<![endif]-->
<!--[if !mso]><!--><!--<![endif]-->
    <style>a:link {color:#197bbd;font-weight:normal;text-decoration:underline;font-style:normal}
a:visited {color:#197bbd;font-weight:normal;text-decoration:underline;font-style:normal}
a:active {color:#197bbd;font-weight:normal;text-decoration:underline;font-style:normal}
a:hover {color:#197bbd;font-weight:normal;text-decoration:underline;font-style:normal}</style><style>@import url(https://static-forms.klaviyo.com/fonts/api/v1/VA7XY5/custom_fonts.css);
#outlook a {
padding: 0
}
body {
margin: 0;
padding: 0;
-webkit-text-size-adjust: 100%;
-ms-text-size-adjust: 100%
}
table, td {
border-collapse: collapse;
mso-table-lspace: 0;
mso-table-rspace: 0
}
img {
border: 0;
line-height: 100%;
outline: none;
text-decoration: none;
-ms-interpolation-mode: bicubic
}
p {
display: block;
margin: 13px 0
}
@media only screen and (min-width: 480px) {
.mj-column-per-100 {
width: 100% !important;
max-width: 100%
}
}
.moz-text-html .mj-column-per-100 {
width: 100% !important;
max-width: 100%
}
@media only screen and (max-width: 480px) {
div.kl-row.colstack div.kl-column {
display: block !important;
width: 100% !important
}
}
.hlb-subblk td {
word-break: normal
}
@media only screen and (max-width: 480px) {
.hlb-wrapper .hlb-block-settings-content {
padding: 9px !important
}
.hlb-logo {
padding-bottom: 9px !important
}
.r2-tbl {
width: 100%
}
.r2-tbl .lnk {
width: 100%
}
.r2-tbl .hlb-subblk:last-child {
padding-right: 0 !important
}
.r2-tbl .hlb-subblk {
padding-right: 10px !important
}
.kl-hlb-stack {
display: block !important;
width: 100% !important;
padding-right: 0 !important
}
.kl-hlb-stack.vspc {
margin-bottom: 9px
}
.kl-hlb-wrap {
display: inline-block !important;
width: auto !important
}
.kl-hlb-no-wrap {
display: table-cell !important
}
.kl-hlb-wrap.nospc.nospc {
padding-right: 0 !important
}
}
@media only screen and (max-width: 480px) {
.component-wrapper .mob-no-spc {
padding-left: 0 !important;
padding-right: 0 !important
}
}
@media only screen and (max-width: 480px) {
.kl-text {
padding-right: 18px !important;
padding-left: 18px !important
}
}
@media only screen and (max-width: 480px) {
.kl-table-subblock.use-legacy-mobile-padding {
padding-left: 9px !important;
padding-right: 9px !important
}
}
@media only screen and (max-width: 480px) {
.kl-split-subblock.top .spacer, .kl-split-subblock.bottom .spacer {
padding: 0 !important
}
.kl-split-subblock.top .spacer {
padding-bottom: 9px !important
}
.kl-split-subblock.top {
display: table-header-group !important;
width: 100% !important
}
.kl-split-subblock.bottom {
display: table-footer-group !important;
width: 100% !important
}
}
@media only screen and (max-width: 480px) {
td.kl-img-base-auto-width {
width: 100% !important
}
}
@media screen and (max-width: 480px) {
.kl-sl-stk {
display: block !important;
width: 100% !important;
padding: 0 0 9px !important;
text-align: center !important
}
.kl-sl-stk.lbls {
padding: 0 !important
}
.kl-sl-stk.spcblk {
display: none !important
}
}
img {
border: 0;
height: auto;
line-height: 100%;
outline: none;
text-decoration: none;
max-width: 100%
}
.root-container {
background-repeat: repeat !important;
background-size: auto !important;
background-position: left top !important
}
.root-container-spacing {
padding-top: 30px !important;
padding-bottom: 20px !important;
font-size: 0 !important
}
.content-padding {
padding-left: 0 !important;
padding-right: 0 !important
}
.content-padding.first {
padding-top: 0 !important
}
.content-padding.last {
padding-bottom: 0 !important
}
@media only screen and (max-width: 480px) {
td.mobile-only {
display: table-cell !important
}
div.mobile-only {
display: block !important
}
table.mobile-only {
display: table !important
}
.desktop-only {
display: none !important
}
}
@media only screen and (max-width: 480px) {
.table-mobile-only {
display: table-cell !important;
max-height: none !important
}
.table-mobile-only.block {
display: block !important
}
.table-mobile-only.inline-block {
display: inline-block !important
}
.table-desktop-only {
max-height: 0 !important;
display: none !important;
mso-hide: all !important;
overflow: hidden !important
}
}
p {
margin-left: 0;
margin-right: 0;
margin-top: 0;
margin-bottom: 0;
padding-bottom: 1em
}
@media only screen and (max-width: 480px) {
.kl-text > div, .kl-table-subblock div, .kl-split-subblock > div {
font-size: 14px !important;
line-height: 1.3 !important
}
}
h1 {
color: #222427;
font-family: "Helvetica Neue", Arial;
font-size: 40px;
font-style: normal;
font-weight: normal;
line-height: 1.1;
letter-spacing: 0;
margin: 0;
margin-bottom: 20px;
text-align: left
}
@media only screen and (max-width: 480px) {
h1 {
font-size: 40px !important;
line-height: 1.1 !important
}
}
h2 {
color: #222427;
font-family: "Helvetica Neue", Arial;
font-size: 32px;
font-style: normal;
font-weight: bold;
line-height: 1.1;
letter-spacing: 0;
margin: 0;
margin-bottom: 16px;
text-align: left
}
@media only screen and (max-width: 480px) {
h2 {
font-size: 32px !important;
line-height: 1.1 !important
}
}
h3 {
color: #222427;
font-family: "Helvetica Neue", Arial;
font-size: 24px;
font-style: normal;
font-weight: bold;
line-height: 1.1;
letter-spacing: 0;
margin: 0;
margin-bottom: 12px;
text-align: left
}
@media only screen and (max-width: 480px) {
h3 {
font-size: 24px !important;
line-height: 1.1 !important
}
}
h4 {
color: #222427;
font-family: "Helvetica Neue", Arial;
font-size: 18px;
font-style: normal;
font-weight: 400;
line-height: 1.1;
letter-spacing: 0;
margin: 0;
margin-bottom: 9px;
text-align: left
}
@media only screen and (max-width: 480px) {
h4 {
font-size: 18px !important;
line-height: 1.1 !important
}
}
@media only screen and (max-width: 480px) {
.root-container {
width: 100% !important
}
.root-container-spacing {
padding: 10px !important
}
.content-padding {
padding-left: 0 !important;
padding-right: 0 !important
}
.content-padding.first {
padding-top: 0 !important
}
.content-padding.last {
padding-bottom: 0 !important
}
.component-wrapper {
padding-left: 0 !important;
padding-right: 0 !important
}
}</style>
  </head>"""
TEMPLATE_ALL_BEFORE_CONTENT = """<div class="root-container" id="bodyTable" style="background-color:#f7f7f7;">
<div class="root-container-spacing">
<table align="center" border="0" cellpadding="0" cellspacing="0" class="kl-section" role="presentation" style="background:#FFFFFF;background-color:#FFFFFF;width:100%;">
<tbody>
<tr>
<td>
<!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="kl-section-outlook" style="width:600px;" width="600" bgcolor="#FFFFFF" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
<div style="margin:0px auto;max-width:600px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;">
<tbody>
<tr>
<td style="direction:ltr;font-size:0px;padding:0px;text-align:center;">
<!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
<div style="background:#ffffff;background-color:#ffffff;margin:0px auto;border-radius:0px 0px 0px 0px;max-width:600px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;background-color:#ffffff;width:100%;border-radius:0px 0px 0px 0px;">
<tbody>
<tr>
<td style="direction:ltr;font-size:0px;padding:20px 0;padding-bottom:0px;padding-left:0px;padding-right:0px;padding-top:0px;text-align:center;">
<!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><![endif]-->
<div class="content-padding first">
<!--[if true]><table border="0" cellpadding="0" cellspacing="0" width="600" style="width:600px;direction:ltr"><tr><![endif]-->
<div class="kl-row colstack" style="display:table;table-layout:fixed;width:100%;">
<!--[if true]><td style="vertical-align:top;width:600px;"><![endif]-->
<div class="kl-column" style="display:table-cell;vertical-align:top;width:100%;">
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper hlb-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="hlb-block-settings-content" style="vertical-align:top;padding-top:9px;padding-right:18px;padding-bottom:9px;padding-left:18px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="top" class="kl-header-link-bar" style="font-size:0px;padding:0px 0px 0px 0px;word-break:break-word;">
<table border="0" cellpadding="0" cellspacing="0" style="color:#000000;font-family:Ubuntu, Helvetica, Arial, sans-serif;font-size:13px;line-height:22px;table-layout:auto;width:100%;border:0;" width="100%">
<tbody>
<tr>
<td align="center" class="hlb-logo" style="display:table-cell;width:100%;padding-bottom:10px;">
<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;">
<tbody>
<tr>
<!--[if true]><td style="width:201px;" bgcolor="transparent"><![endif]-->
<!--[if !true]><!--><td style="width:201px;"><!--<![endif]-->
<a href="https://www.agriland.ie" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline" target="_blank">
<img alt="Agriland logo" src="https://d3k81ch9hvuctc.cloudfront.net/company/VA7XY5/images/def3138c-58f9-441f-a832-2427f0be8074.png" style="display:block;outline:none;text-decoration:none;height:auto;width:100%;background-color:transparent;" width="201"/>
</a>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
<tr>
<td>
<table align="center" cellpadding="0" cellspacing="0" class="r2-tbl" style="table-layout:fixed;" width="100%">
<tr style="text-align:center;">
<td align="center" class="hlb-subblk" style="" valign="middle">
<table border="0" cellpadding="0" cellspacing="0" class="lnk" style="border-collapse:separate;line-height:100%;">
<tr>
<td align="center" bgcolor="transparent" role="presentation" style="border:none;border-radius:0px;cursor:auto;font-style:Normal;mso-padding-alt:5px 5px 5px 5px;background:transparent;" valign="middle">
<a href="https://www.agriland.ie/farming-news/category/beef/" style='color:#3A9948; font-style:Normal; font-weight:400; text-decoration:none; display:inline-block; background:transparent; font-family:"Roboto Condensed", "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; line-height:100%; letter-spacing:0; margin:0; text-transform:none; padding:5px 5px 5px 5px; mso-padding-alt:0; border-radius:0' target="_blank">
Beef
</a>
</td>
</tr>
</table>
</td>
<td align="center" class="hlb-subblk" style="" valign="middle">
<table border="0" cellpadding="0" cellspacing="0" class="lnk" style="border-collapse:separate;line-height:100%;">
<tr>
<td align="center" bgcolor="transparent" role="presentation" style="border:none;border-radius:0px;cursor:auto;font-style:Normal;mso-padding-alt:5px 5px 5px 5px;background:transparent;" valign="middle">
<a href="https://www.agriland.ie/farming-news/category/dairy/" style='color:#3A9948; font-style:Normal; font-weight:400; text-decoration:none; display:inline-block; background:transparent; font-family:"Roboto Condensed", "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; line-height:100%; letter-spacing:0; margin:0; text-transform:none; padding:5px 5px 5px 5px; mso-padding-alt:0; border-radius:0' target="_blank">
Dairy
</a>
</td>
</tr>
</table>
</td>
<td align="center" class="hlb-subblk" style="" valign="middle">
<table border="0" cellpadding="0" cellspacing="0" class="lnk" style="border-collapse:separate;line-height:100%;">
<tr>
<td align="center" bgcolor="transparent" role="presentation" style="border:none;border-radius:0px;cursor:auto;font-style:Normal;mso-padding-alt:5px 5px 5px 5px;background:transparent;" valign="middle">
<a href="https://www.agriland.ie/farming-news/category/sheep/" style='color:#3A9948; font-style:Normal; font-weight:400; text-decoration:none; display:inline-block; background:transparent; font-family:"Roboto Condensed", "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; line-height:100%; letter-spacing:0; margin:0; text-transform:none; padding:5px 5px 5px 5px; mso-padding-alt:0; border-radius:0' target="_blank">
Sheep
</a>
</td>
</tr>
</table>
</td>
<td align="center" class="hlb-subblk" style="" valign="middle">
<table border="0" cellpadding="0" cellspacing="0" class="lnk" style="border-collapse:separate;line-height:100%;">
<tr>
<td align="center" bgcolor="transparent" role="presentation" style="border:none;border-radius:0px;cursor:auto;font-style:Normal;mso-padding-alt:5px 5px 5px 5px;background:transparent;" valign="middle">
<a href="https://www.agriland.ie/farming-news/category/tillage/" style='color:#3A9948; font-style:Normal; font-weight:400; text-decoration:none; display:inline-block; background:transparent; font-family:"Roboto Condensed", "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; line-height:100%; letter-spacing:0; margin:0; text-transform:none; padding:5px 5px 5px 5px; mso-padding-alt:0; border-radius:0' target="_blank">
Tillage
</a>
</td>
</tr>
</table>
</td>
<td align="center" class="hlb-subblk" style="" valign="middle">
<table border="0" cellpadding="0" cellspacing="0" class="lnk" style="border-collapse:separate;line-height:100%;">
<tr>
<td align="center" bgcolor="transparent" role="presentation" style="border:none;border-radius:0px;cursor:auto;font-style:Normal;mso-padding-alt:5px 5px 5px 5px;background:transparent;" valign="middle">
<a href="https://www.agriland.ie/farming-news/category/machinery/" style='color:#3A9948; font-style:Normal; font-weight:400; text-decoration:none; display:inline-block; background:transparent; font-family:"Roboto Condensed", "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; line-height:100%; letter-spacing:0; margin:0; text-transform:none; padding:5px 5px 5px 5px; mso-padding-alt:0; border-radius:0' target="_blank">
Machinery
</a>
</td>
</tr>
</table>
</td>
<td align="center" class="table-desktop-only hlb-subblk" style="" valign="middle">
<table border="0" cellpadding="0" cellspacing="0" class="lnk" style="border-collapse:separate;line-height:100%;">
<tr>
<td align="center" bgcolor="transparent" role="presentation" style="border:none;border-radius:0px;cursor:auto;font-style:Normal;mso-padding-alt:5px 5px 5px 5px;background:transparent;" valign="middle">
<a href="https://www.agriland.ie/farming-news/category/n-ireland/" style='color:#3A9948; font-style:Normal; font-weight:400; text-decoration:none; display:inline-block; background:transparent; font-family:"Roboto Condensed", "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; line-height:100%; letter-spacing:0; margin:0; text-transform:none; padding:5px 5px 5px 5px; mso-padding-alt:0; border-radius:0' target="_blank">
N.Ireland
</a>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
</div>
<!--[if true]></td><![endif]-->
</div>
<!--[if true]></tr></table><![endif]-->
</div>
<!--[if mso | IE]></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
<!--[if mso | IE]></td></tr></table></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
<!--[if mso | IE]></td></tr></table><![endif]-->
</td>
</tr>
</tbody>
</table>
<table align="center" border="0" cellpadding="0" cellspacing="0" class="kl-section" role="presentation" style="width:100%;">
<tbody>
<tr>
<td>
<!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="kl-section-outlook" style="width:600px;" width="600" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
<div style="margin:0px auto;max-width:600px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;">
<tbody>
<tr>
<td style="direction:ltr;font-size:0px;padding:0px;text-align:center;">
<!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
<div style="background:#ffffff;background-color:#ffffff;margin:0px auto;border-radius:0px 0px 0px 0px;max-width:600px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;background-color:#ffffff;width:100%;border-radius:0px 0px 0px 0px;">
<tbody>
<tr>
<td style="direction:ltr;font-size:0px;padding:20px 0;padding-bottom:0px;padding-left:0px;padding-right:0px;padding-top:0px;text-align:center;">
<!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><![endif]-->
<div class="content-padding">
<!--[if true]><table border="0" cellpadding="0" cellspacing="0" width="600" style="width:600px;direction:ltr"><tr><![endif]-->
<div class="kl-row colstack" style="display:table;table-layout:fixed;width:100%;">
<!--[if true]><td style="vertical-align:top;width:600px;"><![endif]-->
<div class="kl-column" style="display:table-cell;vertical-align:top;width:100%;">
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="mob-no-spc" style="background-color:#282828;vertical-align:top;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="left" class="kl-text" style="font-size:0px;padding:0px;padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;word-break:break-word;">
<div style="font-family:'Helvetica Neue',Arial;font-size:14px;font-style:normal;font-weight:400;letter-spacing:0px;line-height:1.3;text-align:left;color:#222427;"><div id="job-header" style="text-align: center;"><span style="font-family: 'Roboto Condensed', 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: bold; font-size: 24px; color: #fffcfc;">Daily News Round Up</span></div></div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
</div>
<!--[if true]></td><![endif]-->
</div>
<!--[if true]></tr></table><![endif]-->
<!--[if true]><table border="0" cellpadding="0" cellspacing="0" width="600" style="width:600px;direction:ltr"><tr><![endif]-->
<div class="kl-row colstack" style="display:table;table-layout:fixed;width:100%;">
<!--[if true]><td style="vertical-align:top;width:600px;"><![endif]-->
<div class="kl-column" style="display:table-cell;vertical-align:top;width:100%;">
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="vertical-align:top;padding-top:9px;padding-right:18px;padding-bottom:9px;padding-left:18px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="left" class="kl-text" style="font-size:0px;padding:0px;padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;word-break:break-word;">
<div style="font-family:'Helvetica Neue',Arial;font-size:14px;font-style:normal;font-weight:400;letter-spacing:0px;line-height:1.3;text-align:left;color:#222427;"><div><span style="font-family: 'Roboto Condensed', 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: bold;">{% today '%Y-%m-%d' as today %} {{ today|format_date_string|date:'d/m/Y' }}</span></div></div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="vertical-align:top;padding-top:9px;padding-right:18px;padding-bottom:9px;padding-left:18px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="left" class="kl-text" style="font-size:0px;padding:0px;padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;word-break:break-word;">
<div style="font-family:'Helvetica Neue',Arial;font-size:14px;font-style:normal;font-weight:400;letter-spacing:0px;line-height:1.3;text-align:left;color:#222427;"><div>"""
TEMPLATE_ALL_AFTER_CONTENT = """</div></div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper kl-text-table-layout" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="vertical-align:top;padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="left" class="kl-text" style="font-size:0px;padding:0px;padding-top:5px;padding-right:10px;padding-bottom:5px;padding-left:10px;word-break:break-word;">
<div style="font-family:'Helvetica Neue',Arial;font-size:14px;font-style:normal;font-weight:400;letter-spacing:0px;line-height:1.3;text-align:left;color:#222427;"><h3 style="text-align: center;"><span style="font-size: 20px;">Download Our App</span></h3></div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
</div>
<!--[if true]></td><![endif]-->
</div>
<!--[if true]></tr></table><![endif]-->
<!--[if true]><table border="0" cellpadding="0" cellspacing="0" width="600" style="width:600px;direction:ltr"><tr><![endif]-->
<div class="kl-row colstack" style="display:table;table-layout:fixed;width:100%;">
<!--[if true]><td style="vertical-align:top;width:600px;"><![endif]-->
<div class="kl-column" style="display:table-cell;vertical-align:top;width:100%;">
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="vertical-align:top;padding-top:9px;padding-right:18px;padding-bottom:9px;padding-left:18px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="left" class="kl-split" style="font-size:0px;padding:0px;word-break:break-word;">
<div style="font-family:Ubuntu, Helvetica, Arial, sans-serif;font-size:13px;line-height:1;text-align:left;color:#000000;"><!--[if true]><table role="presentation" width="100%" style="all:unset;opacity:0;"><tr><![endif]-->
<!--[if false]></td></tr></table><![endif]-->
<div style="display:table;width:100%;">
<!--[if true]><td vertical-align="top" width="50%"><![endif]-->
<!--[if !true]><!--><div class="kl-split-subblock" style="display:table-cell;vertical-align: top;width:50%"><!--<![endif]-->
<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
<tbody>
<tr>
<td class="spacer" style="padding-left:0px;padding-right:18px;" vertical-align="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
<tr>
<td>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" class="" style="font-size:0px;word-break:break-word;">
<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;">
<tbody>
<tr>
<td class="" style="border:0;padding:0;width:175px;" valign="top">
<a href="https://itunes.apple.com/app/apple-store/id912366362?pt=103696803&amp;ct=Email_App_Download&amp;mt=8" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline">
<img alt="Download the Agriland App for iOS" src="https://d3k81ch9hvuctc.cloudfront.net/company/VA7XY5/images/3707aa5f-80e3-47a3-9e76-063cf90d1321.png" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" title="Download the Agriland App for iOS" width="175"/>
</a>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
</tbody>
</table>
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if true]></td><![endif]-->
<!--[if true]><td vertical-align="top" width="50%"><![endif]-->
<!--[if !true]><!--><div class="kl-split-subblock" style="display:table-cell;vertical-align: top;width:50%"><!--<![endif]-->
<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
<tbody>
<tr>
<td class="spacer" style="padding-left:18px;padding-right:0px;" vertical-align="top">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
<tr>
<td>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" class="" style="font-size:0px;word-break:break-word;">
<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;">
<tbody>
<tr>
<td class="" style="border:0;padding:0;width:175px;" valign="top">
<a href="https://play.google.com/store/apps/details?id=com.agriland.agriland&amp;referrer=utm_source%3DAgriland%26utm_medium%3DApp%2520Button%26utm_term%3Dget_the_app_android%26utm_campaign%3DDownload%2520App%2520Email%2520Button" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline">
<img alt="Download the Agriland app for Android" src="https://d3k81ch9hvuctc.cloudfront.net/company/VA7XY5/images/b8d2a39f-875e-4970-a1fa-b8d67a377f62.png" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" title="Download the Agriland app for Android" width="175"/>
</a>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</table>
</td>
</tr>
</table>
</td>
</tr>
</tbody>
</table>
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if true]></td><![endif]-->
</div>
<!--[if true]></tr></table><![endif]--></div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
</div>
<!--[if true]></td><![endif]-->
</div>
<!--[if true]></tr></table><![endif]-->
</div>
<!--[if mso | IE]></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
<!--[if mso | IE]></td></tr></table></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
<!--[if mso | IE]></td></tr></table><![endif]-->
</td>
</tr>
</tbody>
</table>
<table align="center" border="0" cellpadding="0" cellspacing="0" class="kl-section" role="presentation" style="background:#151515;background-color:#151515;width:100%;">
<tbody>
<tr>
<td>
<!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="kl-section-outlook" style="width:600px;" width="600" bgcolor="#151515" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
<div style="margin:0px auto;max-width:600px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;">
<tbody>
<tr>
<td style="direction:ltr;font-size:0px;padding:0px;text-align:center;">
<!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
<div style="background:#ffffff;background-color:#ffffff;margin:0px auto;border-radius:0px 0px 0px 0px;max-width:600px;">
<table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;background-color:#ffffff;width:100%;border-radius:0px 0px 0px 0px;">
<tbody>
<tr>
<td style="border:solid 10px #151515;direction:ltr;font-size:0px;padding:20px 0;padding-bottom:0px;padding-left:0px;padding-right:0px;padding-top:0px;text-align:center;">
<!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><![endif]-->
<div class="content-padding last">
<!--[if true]><table border="0" cellpadding="0" cellspacing="0" width="580" style="width:580px;direction:ltr"><tr><![endif]-->
<div class="kl-row colstack" style="display:table;table-layout:fixed;width:100%;">
<!--[if true]><td style="vertical-align:middle;width:580px;"><![endif]-->
<div class="kl-column" style="display:table-cell;vertical-align:middle;width:100%;">
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="background-color:#151515;vertical-align:top;padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="center" class="kl-image" style="font-size:0px;word-break:break-word;">
<table border="0" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-spacing:0px;">
<tbody>
<tr>
<td class="" style="border:0;padding:0px 0px 0px 0px;background-color:#151515;width:200px;" valign="top">
<a href="https://agrilandmedia.ie/" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline">
<img alt="Agriland Media Company Logo" src="https://d3k81ch9hvuctc.cloudfront.net/company/VA7XY5/images/861d68a9-ec70-414b-981b-7b50b43e1db6.png" style="display:block;outline:none;text-decoration:none;height:auto;font-size:13px;width:100%;" title="Agriland Media Company Logo" width="200"/>
</a>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="background-color:#151515;vertical-align:top;padding-top:18px;padding-right:18px;padding-bottom:18px;padding-left:18px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="center" style="font-size:0px;padding:0px;word-break:break-word;">
<p style="padding-bottom:0; border-top:dashed 1px #808080; font-size:1px; margin:0 auto; width:100%">
</p>
<!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" style="border-top:dashed 1px #808080;font-size:1px;margin:0px auto;width:544px;" role="presentation" width="544px" ><tr><td style="height:0;line-height:0;"> &nbsp;
</td></tr></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="background-color:#151515;vertical-align:top;padding-top:9px;padding-right:9px;padding-bottom:9px;padding-left:9px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td>
<div style="width:100%;text-align:center">
<!--[if true]><table style="all:unset;opacity:0;" border="0" cellpadding="0" cellspacing="0" ><tr><![endif]-->
<!--[if !true]><!--><div class="" style="display:inline-block;padding-right:10px;"><!--<![endif]-->
<!--[if true]><td style="padding-right:10px;"><![endif]-->
<div style="text-align: center;">
<a href="https://www.facebook.com/AgrilandIreland" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline" target="_blank">
<img alt="Facebook" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/subtleinverse/facebook_96.png" style="width:32px;" width="32"/>
</a>
</div>
<!--[if true]></td><![endif]-->
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if !true]><!--><div class="" style="display:inline-block;padding-right:10px;"><!--<![endif]-->
<!--[if true]><td style="padding-right:10px;"><![endif]-->
<div style="text-align: center;">
<a href="https://twitter.com/AgrilandIreland" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline" target="_blank">
<img alt="Twitter" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/subtleinverse/twitter_96.png" style="width:32px;" width="32"/>
</a>
</div>
<!--[if true]></td><![endif]-->
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if !true]><!--><div class="" style="display:inline-block;padding-right:10px;"><!--<![endif]-->
<!--[if true]><td style="padding-right:10px;"><![endif]-->
<div style="text-align: center;">
<a href="https://www.instagram.com/agriland.ie" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline" target="_blank">
<img alt="Instagram" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/subtleinverse/instagram_96.png" style="width:32px;" width="32"/>
</a>
</div>
<!--[if true]></td><![endif]-->
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if !true]><!--><div class="" style="display:inline-block;padding-right:10px;"><!--<![endif]-->
<!--[if true]><td style="padding-right:10px;"><![endif]-->
<div style="text-align: center;">
<a href="https://www.youtube.com/user/AgrilandIreland" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline" target="_blank">
<img alt="YouTube" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/subtleinverse/youtube_96.png" style="width:32px;" width="32"/>
</a>
</div>
<!--[if true]></td><![endif]-->
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if !true]><!--><div class="" style="display:inline-block;"><!--<![endif]-->
<!--[if true]><td style=""><![endif]-->
<div style="text-align: center;">
<a href="https://www.linkedin.com/company/agriland-media-ltd-" style="color:#197bbd; font-style:normal; font-weight:normal; text-decoration:underline" target="_blank">
<img alt="LinkedIn" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/subtleinverse/linkedin_96.png" style="width:32px;" width="32"/>
</a>
</div>
<!--[if true]></td><![endif]-->
<!--[if !true]><!--></div><!--<![endif]-->
<!--[if true]></tr></table><![endif]-->
</div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper" style="font-size:0px;text-align:left;direction:ltr;vertical-align:top;width:100%;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;" width="100%">
<tbody>
<tr>
<td class="" style="background-color:#151515;vertical-align:top;padding-top:8px;padding-right:19px;padding-bottom:8px;padding-left:19px;">
<table border="0" cellpadding="0" cellspacing="0" role="presentation" style="" width="100%">
<tbody>
<tr>
<td align="left" class="kl-text" style="background:#151515;font-size:0px;padding:0px;padding-top:0px;padding-right:0px;padding-bottom:0px;padding-left:0px;word-break:break-word;">
<div style="font-family:'Helvetica Neue',Arial;font-size:14px;font-style:normal;font-weight:400;letter-spacing:0px;line-height:1.3;text-align:left;color:#222427;"><p style="padding-bottom:0; text-align:center"><span style="font-size: 13px; color: #c4c4c4;">No longer want to receive these emails? {% unsubscribe %}.</span><br/><span style="font-size: 13px; color: #c4c4c4;">{{ organization.name }} {{ organization.full_address }}</span></p></div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
</div>
</div>
<!--[if true]></td><![endif]-->
</div>
<!--[if true]></tr></table><![endif]-->
</div>
<!--[if mso | IE]></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
<!--[if mso | IE]></td></tr></table></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
<!--[if mso | IE]></td></tr></table><![endif]-->
</td>
</tr>
</tbody>
</table>
</div>
</div>"""

def create_template(formatted_html, headers):
    template_id = "S2pjUD"
    url = f"https://a.klaviyo.com/api/templates/{template_id}/"

#Building the html content for the API call - this will loop over the items in our news content list and append to payload field. 
    html_content = "<html>" + TEMPLATE_HEADER_STYLE + "<body style='word-spacing:normal;background-color:#f7f7f7';> " + TEMPLATE_ALL_BEFORE_CONTENT

    for entry_html in formatted_html:
        html_content += entry_html['title'] + entry_html['summary'] + entry_html['link']
    
    html_content += TEMPLATE_ALL_AFTER_CONTENT
    html_content += "</body></html>"
#end building 

#Build payload for Klaviyo 
    payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": "test_agriland",
                "html": html_content,
                "text": "Test"
            },
            "id": "S2pjUD"
        }
    }

    #print(payload)
    # Ensure property keys are double-quoted by converting to JSON string and then back to dictionary
    payload = json.dumps(payload)
    # print('THIS IS THE JSON DUMPS LOAD')
    # print(payload)
    # Make the API call to update the template
    response = requests.patch(url, json=json.loads(payload), headers=headers)
    #print(response.text)
    if response.status_code == 200:
        print("Template created successfully.")
    else:
        print(f"Failed to create template. Status code: {response.status_code}")


def create_campaign(account_data):
    create_campaign_data = {
        "data" : {
            "type": "campaign",
            "attributes": {
                "name": f"DAILY NEWS DIGEST",
                "audiences": {
                    "included": [account_data.get('LIST_ID')],
                },
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime" : account_data.get('SEND_TIME')
                    }
                },
                "campaign-messages": {
                "data": [
                {
                    "type": "campaign-message",
                    "attributes": {
                    "channel": "email",
                    "label": "My message name",
                    "content": {
                        "subject": "Buy our product!",
                        "preview_text": "My preview text",
                        "from_email": "store@my-company.com",
                        "from_label": "My Company",
                        "reply_to_email": "reply-to@my-company.com",
                        "cc_email": "cc@my-company.com",
                        "bcc_email": "bcc@my-company.com"
                    },
                    "render_options": {
                        "shorten_links": True
                    }
                    }
                }
                ]
            }
            },
        }
    }

    new_campaign = klaviyo.Campaigns.create_campaign(create_campaign_data)
    campaign_id = new_campaign["data"]["id"]
    message_id = new_campaign["data"]["relationships"]["campaign-messages"]["data"][0]["id"]

    create_campaign_message_assign_template_data =   {
        "data": {
            "type": "campaign-message",
            "id" : message_id,
            "relationships": {
            "template": {
                "data": {
                "type": "template",
                "id":  account_data.get('TEMPLATE_ID')
                }
            }
            }
        }
    }

    print(create_campaign_message_assign_template_data)

    response = klaviyo.Campaigns.create_campaign_message_assign_template(create_campaign_message_assign_template_data)

    create_campaign_send_job_data = {
        "data" :{
            "type": "campaign-send-job",
            "id": campaign_id,
        }
    }

    klaviyo.Campaigns.create_campaign_send_job(create_campaign_send_job_data)



def main():
    extracted_news_content = []

    for news_post in news_data:
        news_url = news_post['link']
        news_headline = news_post["title"]["rendered"]
        news_content = news_post["content"]["rendered"]
        #add something here to grab image URL from 2nd api call key = wp:featuredmedia [[tbd later]]

    #Update our news entry dictionary with the headline, body, url and title of the post
        extracted_content_dict = {
            "title": news_headline,
            "link": news_url,
            "content": clean_html_content(news_content)
        }

        summary_result = generate_summary(openai.api_key, extracted_content_dict)

        extracted_news_content.append(summary_result)

    formatted_html = format_to_html(extracted_news_content)
    create_template(formatted_html, KLAVIYO_HEADERS)
    create_campaign(ACCOUNT_DATA)
    #print(formatted_html)


if __name__ == "__main__":
    main()