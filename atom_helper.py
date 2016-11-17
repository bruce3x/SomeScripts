# coding=utf-8
import argparse

import requests
from lxml import etree


class AtomHelper(object):
    host = 'https://atom.io'

    def __init__(self, keyword, type='packages', verbose=False, **kwargs):
        if type not in ('packages', 'themes'):
            raise ValueError(
                "Parameter 'type' only supports 'packages' or 'themes'.")

        self.kw = keyword
        self.type = type
        self.verbose = verbose
        self.search_url = '{host}/{type}/search?q={kw}'.format(
            host=self.host, type=self.type, kw=self.kw)
        self.items = []

    def extract_item(self, cell):
        """Extract item from cells."""
        target = self.first(cell.xpath(
            './/h4[@class="card-name"]/span/a'), default=None)
        if target is not None:
            title = target.text
            url = self.host + target.get('href')
        else:
            title = url = ''

        desc = self.first(cell.xpath(
            './/span[contains(@class, "card-description")]/text()'))

        download = self.first(cell.xpath(
            './/span[@aria-label="Downloads"]/span[@class="value"]/text()'))
        star = self.first(cell.xpath('.//a[@class="social-count"]/text()'))

        return {
            'title': title,
            'url': url,
            'desc': desc,
            'download': self.number_format(download),
            'star': self.number_format(star),
        }

    def run(self):
        """Do search!"""

        print 'Searching %s ...' % self.kw
        self.items = []

        next_url = self.search_url
        while next_url:
            self.debug('> [GET] %s' % next_url)
            response = requests.get(next_url).text

            html = etree.HTML(response)

            cells = html.xpath('//div[@class="grid-cell"]')

            next_url = self.first(html.xpath('//a[@class="next_page"]/@href'))

            next_url = (self.host + next_url) if next_url else None

            self.items.extend(map(self.extract_item, cells))

        self.debug('Got %d items' % len(self.items))

    def topN(self, N=10, by='download'):
        """Get topN items by download or star count."""
        total = len(self.items)
        N = total if N > total else N

        if by not in ('download', 'star'):
            raise ValueError(
                "Parameter 'by' only supports 'download' or 'star'.")

        return sorted(self.items, key=lambda item: item[by], reverse=True)[:N]

    def debug(self, content):
        """Log something with debug mode."""
        if self.verbose:
            print content

    @staticmethod
    def log_item(item):
        """Log item simply."""
        print 'Title: %s' % item['title']
        print 'Url: %s' % item['url']
        print 'Desc: %s' % item['desc']
        print 'Download: %s' % item['download']
        print 'star: %s' % item['star']
        print '-' * 50

    @staticmethod
    def first(seq, default=''):
        """Extract first item in sequence, or default value."""
        return seq[0] if seq else default

    @staticmethod
    def number_format(num_str):
        """Convert number string like '2,333' to integer."""
        return int(num_str.replace(',', '').strip()) if num_str else num_str


def process_arg():
    parser = argparse.ArgumentParser(
        description='Atom helper to search packages or themes.',
        epilog='Have fun :)')

    parser.add_argument('keyword',
                        nargs='+', help='The keyword to search.')

    parser.add_argument('-n', type=int, default=5,
                        help='Show top N items.(default 5)')
    parser.add_argument('-t', '--type', choices=('packages', 'themes'),
                        default='packages',
                        help='The type to search.(default packages)')
    parser.add_argument('-s', '--sort', choices=('download', 'star'),
                        default='download',
                        help='Sort items by.(default download)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show debug messages.')

    args = vars(parser.parse_args())
    args.update(keyword='+'.join(args['keyword']))
    return args


if __name__ == '__main__':
    args = process_arg()
    helper = AtomHelper(**args)
    helper.run()
    print '=' * 50
    print '*'
    print '* Search %s about "%s"' % (args['type'], args['keyword'])
    print '*'
    print '=' * 50
    map(helper.log_item, helper.topN(N=args['n'], by=args['sort']))
