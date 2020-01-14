"""
Script for generating a total work hours count from a
time sheet.
"""

import argparse
from datetime import datetime, date, time
import pandas as pd
from simple_colors import blue, yellow


def mystrip(datestring):
    "Strips datetimes based on input."
    if len(datestring.split('-')) == 2:
        year = str(date.today().year)
        datestring = year + '-' + datestring
        pattern = '-%m-%d'
    if len(datestring.split('-')) == 3:
        pattern = '%Y-%m-%d'
    return datetime.strptime(datestring, pattern)


# Set up argparse
parser = argparse.ArgumentParser(description='Control timesheets')
subparsers = parser.add_subparsers(
    dest='use',
    help='[a]ppend new entry or make new time[s]heet.')

append_parser = subparsers.add_parser('a', help='a help')
append_parser.add_argument('date', type=str, nargs='?',
                           help='Work date.')
append_parser.add_argument('start_time', type=int, help='From time.')
append_parser.add_argument('end_time', type=int, help='From time.')

sheet_parser = subparsers.add_parser('s', help='s help')
sheet_parser.add_argument('from_date', type=str, help='From date.')
sheet_parser.add_argument('to_date', type=str, nargs='?',
                          help='To date.')
args = parser.parse_args()

df = pd.read_csv('timesheet.csv')

if args.use == 'a':
    # If 'append' option is chosen

    # Add new date
    date_input = args.date if args.date else str(
        datetime.today().date())
    df = df.append({'date': date_input,
                    'start': args.start_time,
                    'stop': args.end_time
                    }, ignore_index=True)
    df = df.sort_values(by='date')

    # Turn date column into datetime
    df.date = df.date.apply(mystrip)

    # Update csv
    df.to_csv('timesheet.csv', index=False)

elif args.use == 's':
    # If timesheet option is chosen

    # Turn args into datetime
    date_time_from = mystrip(args.from_date)
    if args.to_date:  # If to-date supplied
        date_time_to = mystrip(args.to_date)
    else:
        # If to-date not supplied, go until tonight
        today = datetime.now().date()
        tonight = time(hour=23, minute=59)
        date_time_to = datetime.combine(today, tonight)

    # Turn date column into datetime
    df.date = df.date.apply(mystrip)

    # Only dates before from-date and after to-date
    df = df[df.date > date_time_from]
    df = df[df.date < date_time_to]

    df['hours'] = df.stop - df.start  # Count hours
    df['cumsum'] = df.hours.cumsum()  # Get cummulative sum

    hours = sum(df.hours)

    df.to_csv('export_of_timesheet.csv')

    print(df)
    print(blue(f'\nTOTAL HOURS: {hours}', 'bold'))
    print(yellow(
        f'Between {date_time_from.date()} and {date_time_to.date()}'
    ))
