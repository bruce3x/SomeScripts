# coding=utf-8
import os
import re
import sys
import time

from lxml import etree

target_package = 'com.mingdao'
launcher_activity = 'com.mingdao/.presentation.ui.login.WelcomeActivity'

username, password = sys.argv[1:3]

xml_name = 'window_dump.xml'
remote_xml = os.path.join('/sdcard', xml_name)
local_xml = os.path.join(os.path.expanduser('~/Downloads'), xml_name)

# '[42,1023][126,1080]'
bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')


def run(cmd):
    # adb <cmd>
    os.popen('adb %s' % cmd)


def sleep_later(duration=0.5):
    def wrapper(func):
        def do(*args, **kwargs):
            func(*args, **kwargs)
            if 'duration' in kwargs.keys():
                time.sleep(kwargs['duration'])
            else:
                time.sleep(duration)

        return do

    return wrapper


@sleep_later()
def open_app_detail(package):
    print 'Open application detail setting'
    # adb shell am start -a ACTION -d DATA
    intent_action = 'android.settings.APPLICATION_DETAILS_SETTINGS'
    intent_data = 'package:%s' % package

    run('shell am start -a %s -d %s' % (intent_action, intent_data))


def get_dumps():
    print 'Dump window layouts'
    # adb shell uiautomator dump
    run('shell uiautomator dump %s' % remote_xml)
    run('pull %s %s' % (remote_xml, local_xml))


def parse_bounds(text):
    nodes = etree.parse(local_xml)
    return nodes.xpath(u'//node[@text="%s"]/@bounds' % (text))[0]


def random_point_in_bounds(bounds):
    """
    '[42,1023][126,1080]'
    """
    points = bounds_pattern.match(bounds).groups()
    points = map(int, points)
    return (points[0] + points[2]) / 2, (points[1] + points[3]) / 2


@sleep_later()
def click_with_keyword(keyword, dump=True, **kwargs):
    if dump:
        get_dumps()
    bounds = parse_bounds(keyword)
    point = random_point_in_bounds(bounds)

    print 'Click (%d, %d)' % point
    # adb shell input tap 84 1051
    run('shell input tap %d %d' % point)


@sleep_later()
def force_stop(package):
    print 'Force stop %s' % package
    # adb shell am force-stop <package>
    run('shell am force-stop %s' % package)


@sleep_later(1)
def start_activity(activity):
    print 'Start activity %s' % activity
    # adb shell am start -n com.mingdao/.presentation.ui.login.WelcomeActivity
    run('shell am start -n %s' % activity)


@sleep_later(1)
def clear_data(package):
    print 'Clear app data: %s' % package
    # adb shell pm clear <package>
    run('shell pm clear %s' % package)


@sleep_later()
def keyboard_input(text):
    # adb shell input text <string>
    run('shell input text %s' % text)


@sleep_later()
def keyboard_back():
    # adb shell input keyevent 4
    run('shell input keyevent 4')


def main():
    force_stop(target_package)

    clear_data(target_package)

    open_app_detail(target_package)

    click_with_keyword(u'权限')

    click_with_keyword(u'存储空间')

    keyboard_back()

    start_activity(launcher_activity)

    click_with_keyword(u'跳过')

    click_with_keyword(u'手机或邮箱')

    keyboard_input(username)

    click_with_keyword(u'密码', dump=False)

    keyboard_input(password)

    click_with_keyword(u'登录', dump=False)


if __name__ == '__main__':
    main()

    print 'done.'
