# coding=utf-8
import re
import subprocess
import sys
import time

from lxml import etree

target_package = 'com.mingdao'
launcher_activity = 'com.mingdao/.presentation.ui.login.WelcomeActivity'

dump_file = '/sdcard/window_dump.xml'

# '[42,1023][126,1080]'
bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')


def run(cmd):
    # adb <CMD>
    return subprocess.check_output(('adb %s' % cmd).split(' '))


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


def timeit(func):
    def do(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()

        print '[%s] Time spent %.2f seconds.' % (func.__name__, end - start)
    return do


@sleep_later()
def open_app_detail(package):
    print 'Open application detail setting: %s' % package
    # adb shell am start -a ACTION -d DATA
    intent_action = 'android.settings.APPLICATION_DETAILS_SETTINGS'
    intent_data = 'package:%s' % package

    run('shell am start -a %s -d %s' % (intent_action, intent_data))


def dump_layout():
    print 'Dump window layouts'
    # adb shell uiautomator dump <FILE>
    run('shell uiautomator dump %s' % dump_file)


def parse_bounds(text):
    # adb shell cat /sdcard/window_dump.xml
    dumps = run('shell cat %s' % dump_file)
    nodes = etree.XML(dumps)
    return nodes.xpath(u'//node[@text="%s"]/@bounds' % (text))[0]


def point_in_bounds(bounds):
    """
    '[42,1023][126,1080]'
    """
    points = bounds_pattern.match(bounds).groups()
    points = map(int, points)
    return (points[0] + points[2]) / 2, (points[1] + points[3]) / 2


@sleep_later()
def click_with_keyword(keyword, dump=True, **kwargs):
    if dump:
        dump_layout()
    bounds = parse_bounds(keyword)
    point = point_in_bounds(bounds)

    print 'Click "%s" (%d, %d)' % (keyword, point[0], point[1])
    # adb shell input tap <x> <y>
    run('shell input tap %d %d' % point)


@sleep_later()
def force_stop(package):
    print 'Force stop %s' % package
    # adb shell am force-stop <package>
    run('shell am force-stop %s' % package)


@sleep_later(0.5)
def start_activity(activity):
    print 'Start activity %s' % activity
    # adb shell am start -n <activity>
    run('shell am start -n %s' % activity)


@sleep_later(0.5)
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


@timeit
def main():
    username, password = sys.argv[1:3]

    force_stop(target_package)

    clear_data(target_package)

    open_app_detail(target_package)

    click_with_keyword(u'权限')

    click_with_keyword(u'存储空间')

    keyboard_back()

    start_activity(launcher_activity)

    click_with_keyword(u'跳过')

    click_with_keyword(u'手机或邮箱', duration=0)

    keyboard_input(username)

    click_with_keyword(u'密码', dump=False, duration=0)

    keyboard_input(password)

    click_with_keyword(u'登录', dump=False)


if __name__ == '__main__':
    main()
