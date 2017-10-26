import datetime
import os
import requests
import argparse

def date_slash(date):
    return '%04d/%02d/%02d' % date

def parse_date(date_str):
    return (int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))

def from_dateobj(d):
    return (d.year, d.month, d.day)

def today_date():
    return from_dateobj(datetime.datetime.now().date())

def to_dateobj(date):
    return datetime.date(date[0], date[1], date[2])

def find_urls(date):
    start_dates = {
        "nat_pdf": (2012, 7, 6),
        "int_pdf": (2012, 7, 6),
        "jpg": (1851, 9, 18)
    }
    urls = {
        "nat_pdf": "http://www.nytimes.com/images/{date}/nytfrontpage/scannat.pdf",
        "int_pdf": "http://www.nytimes.com/images/{date}/nytfrontpage/scan.pdf",
        "jpg": "http://www.nytimes.com/images/{date}/nytfrontpage/scan.jpg"
    }

    return [url.format(date=date_slash(date)) for (typ, url) in urls.items() if date >= start_dates[typ]]



def download_urls(date, urls, opts):
    sdate = date_slash(date)
    os.makedirs(opts['out'] + '/' + sdate, exist_ok=True)
    for u in urls:
        folderpath = opts['out'] + '/' + sdate + '/'
        filename = u.split('/')[-1]
        if os.path.exists(folderpath+filename) and opts['skipexisting']:
            print("Already downloaded", folderpath+filename)
            continue
        req = requests.get(u)
        if req.ok:
            open(folderpath + filename, 'wb').write(req.content)
            print("Downloaded", filename, "for", date)

def download_date(date, opts):
    urls = find_urls(date)
    download_urls(date, urls, opts)

def download_range(startdate, enddate, opts):
    end = to_dateobj(enddate)
    dateobj = to_dateobj(startdate)
    while dateobj <= end:
        date = from_dateobj(dateobj)
        print(date)
        urls = find_urls(date)
        download_urls(date, urls, opts)
        dateobj += datetime.timedelta(days=1)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='fetch New York Times front pages')
    parser.add_argument('--date', dest='date', help='a date in format YYYYMMDD')
    parser.add_argument('--start-date', dest='startdate', help='a start date in format YYYYMMDD')
    parser.add_argument('--end-date', dest='enddate', help='an end date (inclusive) in format YYYYMMDD')
    parser.add_argument('--skip-existing', action='store_true', dest='skipexisting', help='whether to skip downloads of existing files in output')
    parser.add_argument('--out', dest='out', default='out', help='out directory (default ./out)')

    args = parser.parse_args()
    opts = {'out': args.out, 'skipexisting': args.skipexisting}

    if args.date:
        date = parse_date(args.date)
        print("Downloading date", date)
        download_date(date, opts)

    if args.startdate:
        startdate = parse_date(args.startdate)
        enddate = parse_date(args.enddate) if args.enddate else today_date()
        print("Downloading from", startdate, "to", enddate)
        download_range(startdate, enddate, opts)
