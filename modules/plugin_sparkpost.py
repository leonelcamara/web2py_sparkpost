# -*- coding: utf-8 -*-
# author: Leonel Câmara
"""
Seamlessly integrate Sparkpost API with web2py. 

The Mail class here is mostly a drop in replacement for web2py's built-in one.

The main difference is that it does not support raw emails or encryption.

Depends on python-sparkpost:
https://github.com/SparkPost/python-sparkpost
You can just place the sparkpost folder in your application's modules if you want.


A simple way to use would be to put this in one of your model files (usually db.py):

    from plugin_sparkpost import SparkMail
    mail = SparkMail(api_key='YOUR_API_KEY_HERE', sender='no-reply@example.com')

    auth = Auth(db, host_names=myconf.get('host.names'), mailer=mail)
"""
__version__ = '0.0.2'

import base64
import logging
import os
from gluon.storage import Settings
from gluon.contenttype import contenttype
from gluon.fileutils import read_file
from sparkpost import SparkPost
from gluon._compat import to_native

logger = logging.getLogger("web2py")


class SparkMail(object):
    """
    Use this class instead of web2py's Mail.
    You won't have to change anything in your code and you'll use SparkPost via API.
    """

    class Attachment(object):
        """
        Email attachment

        Args:
            payload: path to file or file-like object with read() method
            filename: name of the attachment stored in message; if set to
                None, it will be fetched from payload path; file-like
                object payload must have explicit filename specified
            content_id: id of the attachment; automatically contained within
                `<` and `>`
            content_type: content type of the attachment; if set to None,
                it will be fetched from filename using gluon.contenttype
                module

        Content ID is used to identify attachments within the html body;
        in example, attached image with content ID 'photo' may be used in
        html message as a source of img tag `<img src="cid:photo" />`.
        """

        def __init__(
                self,
                payload,
                filename=None,
                content_id=None,
                content_type=None):
            if isinstance(payload, str):
                if filename is None:
                    filename = os.path.basename(payload)
                payload = read_file(payload, 'rb')
            else:
                if filename is None:
                    raise Exception('Missing attachment name')
                payload = payload.read()
            self.transmission_dict = {
                'type': content_type or contenttype(filename),
                'name': filename,
                'data': base64.b64encode(payload).decode("ascii")
            }
            self.is_inline = False
            if content_id is not None:
                self.is_inline = True
                self.transmission_dict['name'] = content_id

    def __init__(self, api_key=None, sender=None):
        settings = self.settings = Settings()
        settings.api_key = api_key
        settings.sender = sender
        settings.track_opens = True
        settings.track_clicks = True
        settings.lock_keys = True
        self.result = {}
        self.error = None

    def send(self,
             to,
             subject='[no subject]',
             message='[no message]',
             attachments=None,
             cc=None,
             bcc=None,
             reply_to=None,
             sender=None,
             headers={},
             from_address=None,
             ):

        sender = sender or self.settings.sender

        if to:
            if not isinstance(to, (list, tuple)):
                to = [to]
        else:
            raise Exception('Target receiver address not specified')
        if cc:
            if not isinstance(cc, (list, tuple)):
                cc = [cc]
        if bcc:
            if not isinstance(bcc, (list, tuple)):
                bcc = [bcc]

        if message is None:
            text = html = None
        elif isinstance(message, (list, tuple)):
            text, html = message
        elif message.strip().startswith('<html') and \
                message.strip().endswith('</html>'):
            text = None
            html = message
        else:
            text = message
            html = None

        if attachments is None:
            attachments = []
        elif not isinstance(attachments, (list, tuple)):
            attachments = [attachments]

        attached, inlined = [], []
        for attachment in attachments:
            (attached, inlined)[attachment.is_inline].append(attachment.transmission_dict)

        api_kwargs = {
            'recipients': to,
            'cc': cc,
            'bcc': bcc,
            'text': to_native(text) if text else None,  # The to_native here serves mainly to force LazyT to evaluate
            'html': to_native(html) if html else None,
            'from_email': sender,
            'subject': to_native(subject),
            'track_opens': self.settings.track_opens,
            'track_clicks': self.settings.track_clicks,
        }
        if attached:
            api_kwargs['attachments'] = attached
        if inlined:
            if not html:
                raise Exception('Inline images require HTML content')
            api_kwargs['inline_images'] = inlined

        result = {}
        try:
            sp = SparkPost(self.settings.api_key)
            result = sp.transmissions.send(**api_kwargs)
        except Exception as e:
            logger.warning('Mail.send failure:%s' % e)
            self.result = result
            self.error = e
            return False
        self.result = result
        self.error = None
        return True
