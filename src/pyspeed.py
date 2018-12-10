#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import time
import json
import logging
import speedtest
import schedule
import plotly.offline as poffline
import plotly.graph_objs as go

from jsonschema import validate

__author__ = 'D3473R <d3473r@gmail.com>'

settings = None


def check_file():
    if os.path.exists(settings['speed_file']):
        if not os.path.isfile(settings['speed_file']):
            os.remove(settings['speed_file'])
            __create_file()
    else:
        __create_file()


def __create_file():
    f = open(settings['speed_file'], 'w')
    f.close()


def test_speed():
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()

    logging.info(s.results.json())

    with open(settings['speed_file'], 'a') as json_file:
        json_file.write('{}\n'.format(s.results.json()))

    plot()


def plot():
    x_date = []
    y_download = []
    y_download_text = []
    y_upload = []
    y_upload_text = []
    y_ping = []
    y_ping_text = []

    a = 0

    with open(settings['speed_file'], 'r') as f:
        for line in f:

            if not line == '':
                j_tmp = json.loads(line)
                x_date.append(j_tmp['timestamp'])
                y_download.append(mbit(j_tmp['download']))
                y_download_text.append(
                    'Download Speed: ' + str(mbit(j_tmp['download'])) + ' Mbit/s')
                y_upload.append(mbit(j_tmp['upload']))
                y_upload_text.append('Upload Speed: ' +
                                     str(mbit(j_tmp['upload'])) + ' Mbit/s')
                y_ping.append(j_tmp['ping'])
                y_ping_text.append('Ping: ' + str(j_tmp['ping']) + ' sec')

            a += 1

    download = go.Scatter(
        x=x_date,
        y=y_download,
        text=y_download_text,
        marker=dict(
            color=settings['download']['color']
        ),
        name='Download'
    )
    upload = go.Scatter(
        x=x_date,
        y=y_upload,
        text=y_upload_text,
        marker=dict(
            color=settings['upload']['color']
        ),
        name='Upload'
    )
    ping = go.Scatter(
        x=x_date,
        y=y_ping,
        text=y_ping_text,
        marker=dict(
            color=settings['ping']['color']
        ),
        name='Ping'
    )

    data = [download, upload, ping]
    layout = go.Layout(
        barmode='group',
        shapes=[
            {
                'type': 'line',
                'xref': 'paper',
                'yref': 'y',
                'x0': 0,
                'y0': settings['download']['target'],
                'x1': len(x_date),
                'y1': settings['download']['target'],
                'line': {
                    'color': settings['download']['color'],
                    'width': 2,
                    'dash': 'dash',
                },
            },
            {
                'type': 'line',
                'xref': 'paper',
                'yref': 'y',
                'x0': 0,
                'y0': settings['upload']['target'],
                'x1': len(x_date),
                'y1': settings['upload']['target'],
                'line': {
                    'color': settings['upload']['color'],
                    'width': 2,
                    'dash': 'dash',
                },
            }
        ]
    )

    fig = go.Figure(data=data, layout=layout)
    poffline.plot(fig, filename=settings['html_file'], auto_open=False)


def mbit(f):
    try:
        return round(f / (1024 * 1024), 2)
    except ValueError as e:
        print(e)


def read_settings():
    global settings

    with open('settings/schema.json', 'r') as schema_file:
        schema = json.load(schema_file)
    with open('settings/settings.json', 'r') as settings_file:
        settings = json.load(settings_file)
    validate(settings, schema)


def main():
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    read_settings()
    check_file()

    schedule.every().hour.do(test_speed).run()
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
