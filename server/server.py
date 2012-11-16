#!/usr/bin/env python
#
# Based off example code found in the Tornado package, and code from
# the tinaja labs xbee package.

import datetime, logging, math, os, random, serial, sys, syslog, time, uuid

import tornado.escape
import tornado.ioloop
import tornado.options
from tornado.options import define, options
import tornado.web
import tornado.websocket

from xbee import xbee

define("port", default=8888, help="run on the given port", type=int)

def log_data_file(plant_num):
  return "sensor-data/" + plant_num + ".log"

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        (r"/plant/(.*)", WaterDataSocketHandler),
        (r"/sensorupdated/(.*)/(.*)", SensorUpdatedHandler),
        (r"/*", MainHandler),
        ]
    settings = dict(
        cookie_secret="it'sarandomcookiesecrethopefullynooneguessesit!",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        autoescape=None,
        )
    tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("index.html", messages=[])

class SensorUpdatedHandler(tornado.web.RequestHandler):
  def get(self, plant_num, value):
    WaterDataSocketHandler.send_latest_data(plant_num, value)

class WaterDataSocketHandler(tornado.websocket.WebSocketHandler):

  clients = {}
  instructions = []

  def allow_draft76(self):
    # for iOS 5.0 Safari
    return True

  def open(self, plant_num):
    plant_num = plant_num.strip('?plant=_')
    WaterDataSocketHandler.clients[plant_num] = self
    self.plant_num = plant_num
    logging.info("got client for plant " + plant_num)
    WaterDataSocketHandler.send_all_data(plant_num)

  def on_close(self):
    del WaterDataSocketHandler.clients[self.plant_num]

  @classmethod
  def update_cache(cls, instruction):
    cls.instructions.append(instruction)

  @classmethod
  def send_all_data(cls, plant_num):
    data = 'hi shiry'
    try:
      data_file = open(log_data_file(plant_num), 'r')
      data = {}
      for line in data_file:
        timestamp, reading = line.strip().split()
        data[timestamp] = reading
    except IOError:
      pass

    logging.info(data)

    try:
      cls.clients[plant_num].write_message(data);
    except:
      logging.error("Error sending message", exc_info=True)

  @classmethod
  def send_latest_data(cls, plant_num, sensor_reading):
    if not plant_num in cls.clients:
      return

    client = cls.clients[plant_num]
    try:
      client.write_message(sensor_reading);
    except:
      logging.error("Error sending message", exc_info=True)

  def on_message(self, instruction):
    logging.info("got message %r", instruction)
    parsed = tornado.escape.json_decode(instruction)
    WaterDataSocketHandler.update_cache(parsed)

def main():
  # look into
  # https://github.com/tavendo/AutobahnPython/tree/master/examples/wamp/serial2ws
  tornado.options.parse_command_line()
  app = Application()
  app.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
