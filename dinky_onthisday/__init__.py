import pluggy
from datetime import datetime
import requests
import textwrap
import random
from PIL import Image, ImageFont, ImageDraw
import pkg_resources
from io import BytesIO

from dinky.layouts.layout_configuration import Zone

hookimpl = pluggy.HookimplMarker("dinky")

class DinkyOnThisDayPlugin:
    primary_color = "#f4a261"

    def _get_events(self):
        today = datetime.now()
        response = requests.get(
            url=f'https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/selected/{today.month}/{today.day}'
        )
        return response.json()['selected']


    @hookimpl
    def dinky_draw_zone(self, zone: Zone):
        events = self._get_events()
        max_events = int(zone.height * zone.height / 15000)
        if len(events) > max_events:
            events = random.sample(events, max_events)
        events = sorted(events, key=lambda event: event['year'])
        text = "\n".join([f"{event['year']}: {event['text']}" for event in events])
        wrapper = textwrap.TextWrapper(width=int(0.14 * (zone.width - 2 * zone.padding)), max_lines=3, subsequent_indent='    ')
        text = "\n".join([wrapper.fill(f"{event['year']}: {event['text']}") for event in events])
        im = Image.new('RGB', (zone.width, zone.height), (255, 255, 255))
        draw = ImageDraw.Draw(im)

        font_data = pkg_resources.resource_stream('dinky_onthisday', 'fonts/Roboto-Regular.ttf')
        font_bytes = BytesIO(font_data.read())
        font_header = ImageFont.truetype(font_bytes, 36)
        font_bytes.seek(0)
        font_regular = ImageFont.truetype(font_bytes, 14)

        draw.rectangle((zone.padding, zone.padding, zone.width-zone.padding, zone.padding + 55), fill=self.primary_color)
        draw.text((zone.padding + 5, zone.padding + 5), "On This Day", font=font_header, fill="white")
        draw.multiline_text((zone.padding + 5, zone.padding + 5 + 55), text, font=font_regular, fill="black")
        return im