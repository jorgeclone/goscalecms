import re
import os
import simplejson
import datetime
import urllib2
from gdata.calendar import client
from goscale import models as goscale_models
from goscale import utils
from goscale import conf
from goscale import decorators
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext as _


class Calendar(goscale_models.GoscaleCMSPlugin):
    """
    Google Calendar Events
    """
    url = models.CharField(max_length=250, verbose_name=_('Calendar feed URL'),
        help_text=_('user: https://plus.google.com/photos/114610201247248895941/<br/> \
            album: https://plus.google.com/photos/114610201247248895941/albums/5319044261264143137'))
    show_datepicker = models.BooleanField(default=False, verbose_name=_('Show date picker'),
        help_text=_('If set slideshow will start automatically.'))
    show_past = models.BooleanField(default=False, verbose_name=_('Show past events'),
        help_text=_('If set slideshow will start automatically.'))
    id = None

    def _get_data(self):
        cal_client = client.CalendarClient()
        feed = cal_client.get_calendar_event_feed(uri=self.url+'?hl=en')
        events = []
        for i, an_event in enumerate(feed.entry):
            events.append(an_event)
        #        events = self._changeEventsTime(events)
        return events

    def _get_entry_link(self, entry):
        return entry.link[0].href

    def _store_post(self, stored_entry, entry):
        location = None
#        a_when = None
#        for a_when in entry.when:
#            for a_where in entry.where:
#                if a_where.value_string is not None:
#                    location = a_where.value_string
#        if entry.content.text != None:
#            stored_entry.description = entry.content.text
        attributes = {
            'event_id': entry.link[0].href.split('eid=')[1],
            'event_id2': entry.id.text,
        }
        for attr in entry.content.text.split('<br />'):
            if ':' not in attr:
                continue
            [key, val] = attr.split(':', 1)
            attributes[key.strip().lower().replace(' ', '_')] = val.strip()
        stored_entry.title = entry.title.text
        stored_entry.link = self._get_entry_link(entry)
        stored_entry.updated = datetime.datetime.strptime(entry.updated.text, '%Y-%m-%dT%H:%M:%S.%fZ')
        stored_entry.published = datetime.datetime.strptime(entry.published.text, '%Y-%m-%dT%H:%M:%S.%fZ')
        stored_entry.author = entry.author[0].name.text
        stored_entry.attributes = simplejson.dumps(attributes)
        stored_entry.description = attributes.get('event_description')
        return super(Calendar, self)._store_post(stored_entry)

signals.post_save.connect(goscale_models.update_posts, sender=Calendar)