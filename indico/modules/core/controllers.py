# This file is part of Indico.
# Copyright (C) 2002 - 2017 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import requests
from flask import flash, jsonify, redirect, request, session
from packaging.version import Version
from pytz import common_timezones_set
from werkzeug.urls import url_join

import indico
from indico.core.config import config
from indico.core.settings import PrefixSettingsProxy
from indico.legacy.webinterface.rh.base import RH
from indico.modules.admin import RHAdminBase
from indico.modules.cephalopod import cephalopod_settings
from indico.modules.core.forms import SettingsForm
from indico.modules.core.settings import core_settings, social_settings
from indico.modules.core.views import WPSettings
from indico.util.i18n import _
from indico.web.flask.util import url_for
from indico.web.forms.base import FormDefaults


class RHSettings(RHAdminBase):
    """General settings"""

    def _get_cephalopod_data(self):
        if not cephalopod_settings.get('joined'):
            return None, {'enabled': False}

        url = url_join(config.COMMUNITY_HUB_URL,
                       'api/instance/{}'.format(cephalopod_settings.get('uuid')))
        data = {'enabled': cephalopod_settings.get('joined'),
                'contact': cephalopod_settings.get('contact_name'),
                'email': cephalopod_settings.get('contact_email'),
                'url': config.BASE_URL,
                'organization': core_settings.get('site_organization')}
        return url, data

    def _process(self):
        proxy = PrefixSettingsProxy({'core': core_settings, 'social': social_settings})
        form = SettingsForm(obj=FormDefaults(**proxy.get_all()))
        if form.validate_on_submit():
            proxy.set_multi(form.data)
            flash(_('Settings have been saved'), 'success')
            return redirect(url_for('.settings'))

        cephalopod_url, cephalopod_data = self._get_cephalopod_data()
        show_migration_message = cephalopod_settings.get('show_migration_message')
        return WPSettings.render_template('settings.html', 'settings',
                                          form=form,
                                          core_settings=core_settings.get_all(),
                                          social_settings=social_settings.get_all(),
                                          cephalopod_url=cephalopod_url,
                                          cephalopod_data=cephalopod_data,
                                          show_migration_message=show_migration_message)


class RHChangeTimezone(RH):
    """Update the session/user timezone"""

    def _process(self):
        mode = request.form['tz_mode']
        tz = request.form.get('tz')
        update_user = request.form.get('update_user') == '1'

        if mode == 'local':
            session.timezone = 'LOCAL'
        elif mode == 'user' and session.user:
            session.timezone = session.user.settings.get('timezone', config.DEFAULT_TIMEZONE)
        elif mode == 'custom' and tz in common_timezones_set:
            session.timezone = tz

        if update_user:
            session.user.settings.set('force_timezone', mode != 'local')
            if tz:
                session.user.settings.set('timezone', tz)

        return '', 204


class RHChangeLanguage(RH):
    """Update the session/user language"""

    def _process(self):
        language = request.form['lang']
        session.lang = language
        if session.user:
            session.user.settings.set('lang', language)
        return '', 204


class RHVersionCheck(RHAdminBase):
    """Check the installed indico version against pypi"""

    def _process(self):
        data = requests.get('https://pypi.python.org/pypi/indico/json').json()
        current_version = Version(indico.__version__)
        if current_version.is_prerelease:
            # if we are on a prerelease, get the latest one even if it's also a prerelease
            latest_version = Version(data['info']['version'])
        else:
            # if we are stable, get the latest stable version
            versions = map(Version, data['releases'])
            latest_version = max(v for v in versions if not v.is_prerelease)
        return jsonify(current_version=unicode(current_version), latest_version=unicode(latest_version),
                       outdated=(current_version < latest_version))
