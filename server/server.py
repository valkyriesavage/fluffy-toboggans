#!/usr/bin/env python
#
# Based off example code found in the Tornado package, and code from
# the tinaja labs xbee package.

import datetime, json, logging, os, serial, sys, syslog, time, uuid

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

def instructions_data_file(plant_num):
  return "instructions-data/" + plant_num + ".log"

def translate_instruction(instruction):
  translate = json.loads(instruction)
  if 'manual_percent_moisture' in translate:
    translate = "M" + chr(int(translate['manual_percent_moisture'] + "0")) +\
                      chr(0x54)
  else:
    translate = "A" +\
                chr(int(translate['auto_percent_moisture_low'] + "0")) +\
                chr(int(translate['auto_percent_moisture_high'] + "0"))
  return translate + '\n'

def touch(fname, times=None):
  # from stackoverflow question 1158076
  with file(fname, 'a'):
    os.utime(fname, times)

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        (r"/plant/(.*)", WaterDataSocketHandler),
        (r"/sensorupdated/(.*)/(.*)", SensorUpdatedHandler),
        (r"/tomatoes", TomatoesHandler),
        (r"/", SplashHandler),
        ]
    settings = dict(
        cookie_secret="it'sarandomcookiesecrethopefullynooneguessesit!",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        autoescape=None,
        )
    tornado.web.Application.__init__(self, handlers, **settings)


class SplashHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("splash.html", messages=[])

class TomatoesHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("tomatoes.html", messages=[])

class SensorUpdatedHandler(tornado.web.RequestHandler):
  def get(self, plant_num, value):
    WaterDataSocketHandler.send_latest_data(plant_num, value)

class WaterDataSocketHandler(tornado.websocket.WebSocketHandler):

  clients = {}

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
  def send_all_data(cls, plant_num):
    data = 'hi shiry'
    try:
      data_file = open(log_data_file(plant_num), 'r')
      data = []
      for line in data_file:
        try:
          timestamp, reading = line.strip().split()
        except ValueError, e:
          continue
        data.append({timestamp: reading})

    except IOError:
      pass

    logging.info("sent data")

    try:
      cls.clients[plant_num].write_message(tornado.escape.json_encode(data))
    except:
      logging.error("Error sending message", exc_info=True)

  @classmethod
  def send_latest_data(cls, plant_num, sensor_reading):
    if not plant_num in cls.clients:
      return
    try:
      data = [{str(time.time()): str(sensor_reading)}]
      cls.clients[plant_num].write_message(tornado.escape.json_encode(data))
    except:
      logging.error("Error sending message", exc_info=True)

  def on_message(self, instruction):
    logging.info("got message %r", instruction)
    touch(instructions_data_file(self.plant_num))
    instructions_file = open(instructions_data_file(self.plant_num), 'w')
    instructions_file.write(translate_instruction(instruction))
    instructions_file.close()

def main():
  tornado.options.parse_command_line()
  app = Application()
  app.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
