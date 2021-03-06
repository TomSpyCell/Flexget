from __future__ import unicode_literals, division, absolute_import
import logging

from flexget import plugin
from flexget.event import event

log = logging.getLogger('urlrewrite_redirect')


class UrlRewriteRedirect(object):
    """Rewrites urls which actually redirect somewhere else."""
    def __init__(self):
        self.processed = set()

    def on_task_start(self):
        self.processed = set()

    def url_rewritable(self, task, entry):
        if not any(entry['url'].startswith(adapter) for adapter in task.requests.adapters):
            return False
        return entry['url'] not in self.processed

    def url_rewrite(self, task, entry):
        try:
            # Don't accidentally go online in unit tests
            if task.manager.unit_test:
                return
            r = task.requests.head(entry['url'])
            if 300 <= r.status_code < 400 and 'location' in r.headers:
                entry['url'] = r.headers['location']
        except Exception:
            pass
        finally:
            # Make sure we don't try to rewrite this url again
            self.processed.add(entry['url'])


@event('plugin.register')
def register_plugin():
    plugin.register(UrlRewriteRedirect, 'urlrewrite_redirect', groups=['urlrewriter'], api_ver=2)
