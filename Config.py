"""Loads configuration data from "config.json"."""

import json


class KeyInfo:
    """Provides information about key filenames and colors."""

    def __init__(self):
        """Load info from "key-config.json"."""

        try:
            with open('key-config.json', 'r') as f:
                self._info = json.load(f)

        except Exception as e:
            print(e)
            self._info = dict()

        if not 'primary_key' in self._info.keys() \
        or not isinstance(self._info['primary_key'], str):
            self._info['primary_key'] = '*'

        if not 'secondary_keys' in self._info.keys() \
        or not isinstance(self._info['secondary_keys'], list):
            self._info['secondary_keys'] = []

        # Colors
        self.primary_key_color = '#00FF00'
        self.secondary_key_color = '#0000FF'
        self.error_color = '#FF0000'


    def get_key_color(self, filename):
        """Determine the color based on the key."""

        filename = filename.lower()

        if not filename:
            return None

        elif filename == self._info['primary_key']:
            return self.primary_key_color

        elif filename in self._info['secondary_keys']:
            return self.secondary_key_color

        else:
            return self.error_color
