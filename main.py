#!/bin/python3

'''
"Smart DCA backtest" - Smart Dollar Cost Averaging backtest
Copyright (C) 2022 Andrea Varesio <https://www.andreavaresio.com/>
Source Code: <https://github.com/andrea-varesio/smart-dca-backtest>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import argparse
import asyncio
import csv
import datetime
import hashlib
import os
import pathlib
import random
import sys
import time
import urllib.request

import pandas
import yfinance

VERSION = 20221209.02

cwd = os.path.dirname(os.path.realpath(__file__))
tiers = ['tier_n3', 'tier_n2', 'tier_n1', 'tier_00', 'tier_p1', 'tier_p2', 'tier_p3']
header = [
    'Trial', 'Value', 'Inv Total', 'Gain', 'All-time-high Drawdown', 'Max Drawdown',
    'Time to Recovery',' Ranges', 'Multipliers'
]

def parse_arguments():
    '''Parse arguments'''

    copy = 'Smart DCA backtest - Copyright (C) 2022 Andrea Varesio <https://www.andreavaresio.com/>'
    arg = argparse.ArgumentParser(description=copy)

    asset = arg.add_mutually_exclusive_group()
    ranges = arg.add_mutually_exclusive_group()
    mult = arg.add_mutually_exclusive_group()

    arg.add_argument('-l', '--license', help='show License', action='store_true')
    arg.add_argument('-d', '--disclaimer', help='show Disclaimer', action='store_true')

    arg.add_argument('-v', '--version', help='show current version', action='store_true')
    arg.add_argument('-u', '--update', help='find new versions and update', action='store_true')

    asset.add_argument('-a', '--asset', help='asset to analyze [Default: SWDA.MI]', type=str)
    asset.add_argument('--sp500', help='S&P 500 (avail: 1927) [^GSPC]', action='store_true')
    asset.add_argument('--dji', help='DJI (avail: 1992) [^DJI]', action='store_true')
    asset.add_argument('--nasdaq', help='NASDAQ Comp. (avail: 1971) [^IXIC]', action='store_true')
    asset.add_argument('--nyse', help='NYSE Comp. (avail: 1965) [^NYA]', action='store_true')
    asset.add_argument('--r2000', help='Russell 2000 (avail: 1987) [^RUT]', action='store_true')
    asset.add_argument('--ftse100', help='FTSE 100 (avail: 1984) [^FTSE]', action='store_true')
    asset.add_argument('--n225', help='Nikkei 225 (avail: 1965) [^N225]', action='store_true')
    asset.add_argument('--ftsemib', help='FTSE MIB (avail: 1997) [FTSEMIB.MI]', action='store_true')

    arg.add_argument('-p', '--period', help='years to backtest [Default: ALL]', type=int)

    arg.add_argument('-M', '--max-mult', help='maximum multiplier [Default: 2]', type=float)
    arg.add_argument('-m', '--min-mult', help='minimum multiplier [Default: 0.25]', type=float)
    arg.add_argument('-fM', '--force-max', help='force max multiplier limit', action='store_true')
    arg.add_argument('-fm', '--force-min', help='force min multiplier limit', action='store_true')
    mult.add_argument('-mi', '--mult-incr', help='multiplier increment [Default: 0.25]', type=float)
    mult.add_argument('-rm', '--rand-mult', help='generate random multipliers', action='store_true')

    arg.add_argument('-fn', '--force-neg', help='force values < 0 for ranges', action='store_true')
    ranges.add_argument('-t', '--trials', help='random ranges trials [Default: 10000]', type=int)
    ranges.add_argument('-ir', '--incr-ranges', help='use incremental ranges', action='store_true')

    arg.add_argument('-O', '--output', help='path to output directory', type=str)
    arg.add_argument('-q', '--quiet', help='disable verbosity', action='store_true')
    arg.add_argument('-T', '--time', help='measure script execution time', action='store_true')

    return arg.parse_args()

def show_license():
    '''Show License'''

    print('*' * 86)
    print('"Smart DCA backtest" - Smart Dollar Cost Averaging backtest')
    print('Copyright (C) 2022 Andrea Varesio <https://www.andreavaresio.com/>.')
    print('Source Code: <https://github.com/andrea-varesio/smart-dca-backtest>')
    print('\nThis program comes with ABSOLUTELY NO WARRANTY')
    print('This is free software, and you are welcome to redistribute it under certain conditions')
    print('Full license available at <https://github.com/andrea-varesio/smart-dca-backtest>')
    print('*' * 86)

def show_disclaimer():
    '''Show Disclaimer'''

    print('DISCLAIMER:')
    print(f"{pathlib.Path(os.path.join(cwd, 'DISCLAIMER')).read_text(encoding='utf-8')}")
    print('*' * 100)

def run_update():
    '''Check for new versions and prompt to update'''

    baseurl = 'https://raw.githubusercontent.com/andrea-varesio/smart-dca-backtest/main/'

    filename = os.path.basename(os.path.realpath(__file__))
    url = baseurl + filename
    digests_url = url + '.DIGESTS.asc'

    with urllib.request.urlopen(digests_url) as digests:
        for line in digests:
            if line.decode().startswith('version', 14):
                version_origin = str(line.decode()[22:-2])
                if VERSION == version_origin:
                    print('There are currently no updates available.')
                    sys.exit(0)
            elif line.decode().startswith('sha512sum', 2):
                sha512_origin = str(line.decode()[len('$ sha512sum: '):])
                break
            sha512_origin = None

    if not sha512_origin:
        raise ValueError('sha512sum not found! Hash could not be verified!')

    with urllib.request.urlopen(url) as update_file:
        update = update_file.read()
        sha512_file = hashlib.sha512(update).hexdigest()

        if sha512_file == sha512_origin:
            with open('main.py', 'wb') as main_file:
                main_file.write(update)
        else:
            raise ValueError('sha512sum does not match!')

    args = parse_arguments()
    if not args.quiet:
        print('Update complete')

def run_checks():
    '''Run required checks'''

    args = parse_arguments()
    status = 0

    if args.license:
        show_license()
        status += 1

    if args.disclaimer:
        show_disclaimer()
        status += 1

    if args.version:
        print('Version: ' + str(VERSION))
        status += 1

    if args.update:
        run_update()
        status += 1

    if status > 0:
        sys.exit(0)

def get_output_dir(asset):
    '''Get output directory'''

    args = parse_arguments()

    dir_main = 'smart-dca-backtest'
    dir_sub = f'{asset}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    dir_path = os.path.join(dir_main, dir_sub)

    if not args.output:
        return os.path.join(pathlib.Path.home(), dir_path)

    if os.path.isdir(args.output):
        if args.output.startswith('./'):
            output_dir_root = os.path.join(os.getcwd(), args.output.replace('./', '', 1))
        elif args.output == '.':
            output_dir_root = args.output.replace('.', os.getcwd())
        else:
            output_dir_root = args.output

        return os.path.join(output_dir_root, dir_path)

    raise FileNotFoundError('Invalid output path!')

def get_trial_path(output_dir, trial):
    '''Return trial path'''

    if trial == 0:
        return os.path.join(output_dir, 'dca.csv')

    return os.path.join(output_dir, 'trials', f'trial_{trial}.csv')

def get_asset():
    '''Get asset to analyze'''

    args = parse_arguments()

    if args.asset:
        asset = args.asset
    elif args.sp500:
        asset = '^GSPC'
    elif args.dji:
        asset = '^DJI'
    elif args.nasdaq:
        asset = '^IXIC'
    elif args.nyse:
        asset = '^NYA'
    elif args.r2000:
        asset = '^RUT'
    elif args.ftse100:
        asset = '^FTSE'
    elif args.n225:
        asset = '^N225'
    elif args.ftsemib:
        asset = 'FTSEMIB.MI'
    else:
        asset = 'SWDA.MI'

    return asset

def get_period():
    '''Get time period to analyze'''

    args = parse_arguments()

    if not args.period:
        return int(datetime.datetime.now().strftime('%Y')) - 999

    return int(datetime.datetime.now().strftime('%Y')) - args.period

def get_data(asset, output_dir):
    '''Get historical data and save it to historical.csv, return start_date and data'''

    date = datetime.datetime.now().strftime('%Y-%m-%d')
    hist_raw = os.path.join(output_dir, 'historical_raw.csv')
    hist = os.path.join(output_dir, 'historical.csv')

    data_raw_yf = yfinance.download(asset, f'{get_period()}-01-01', date, progress=False)
    data_raw_yf.to_csv(hist_raw)

    tz_format = '%Y-%m-%d %H:%M:%S%z'
    start_date = datetime.datetime.strptime(pandas.read_csv(hist_raw)['Date'][0], tz_format).date()

    with (
        open(hist_raw, 'r', encoding='utf-8') as data_raw,
        open(hist, 'w', encoding='utf-8') as data_clean
    ):

        csv_data = csv.writer(data_clean,delimiter=',')
        csv_data.writerow(['Date', 'Close'])

        current_month = None

        for line in csv.reader(data_raw):
            try:
                date = datetime.datetime.strptime(line[0][:19], "%Y-%m-%d %H:%M:%S")

                if date.month != current_month:
                    current_month = date.month
                    csv_data.writerow([line[0], line[4]])
            except ValueError:
                pass

    return start_date, pandas.read_csv(hist)

def gen_multipliers():
    '''Generate list of multipliers'''

    args = parse_arguments()

    if args.max_mult:
        maxm = args.max_mult
    else:
        maxm = 2

    if args.min_mult:
        minm = args.min_mult
    else:
        minm = 0.25

    if args.rand_mult:
        if not args.force_max:
            maxm = round(random.uniform(1, maxm), 2)

        if not args.force_min:
            minm = round(random.uniform(minm, 1), 2)

        n2_mult = round(random.uniform(1, maxm), 2)
        n1_mult = round(random.uniform(1, n2_mult), 2)

        p2_mult = round(random.uniform(1, minm), 2)
        p1_mult = round(random.uniform(1, p2_mult), 2)

        return dict(zip(tiers, [maxm, n2_mult, n1_mult, 1, p1_mult, p2_mult, minm]))

    if args.mult_incr:
        incr = args.mult_incr
    else:
        incr = 0.25

    if not args.force_max and maxm > 1 + (incr * 3):
        maxm = 1 + (incr * 3)

    if not args.force_min and minm < 1 - (incr * 3):
        minm = 1 - (incr * 3)

    return dict(zip(tiers, [maxm, 1+(incr*2), 1+incr, 1, 1-incr, 1-(incr*2), minm]))

def get_multiplier(delta, multipliers, ranges):
    '''Get multiplier from avg_nav'''

    if delta < ranges['tier_n3'][1]:
        multiplier = multipliers['tier_n3']
    elif ranges['tier_n2'][0] <= delta < ranges['tier_n2'][1]:
        multiplier = multipliers['tier_n2']
    elif ranges['tier_n1'][0] <= delta < ranges['tier_n1'][1]:
        multiplier = multipliers['tier_n1']
    elif ranges['tier_00'][0] <= delta < ranges['tier_00'][1]:
        multiplier = multipliers['tier_00']
    elif ranges['tier_p1'][0] <= delta < ranges['tier_p1'][1]:
        multiplier = multipliers['tier_p1']
    elif ranges['tier_p2'][0] <= delta < ranges['tier_p2'][1]:
        multiplier = multipliers['tier_p2']
    elif ranges['tier_p3'][0] <= delta:
        multiplier = multipliers['tier_p3']

    return multiplier

def get_drawdown(trial_path):
    '''Calculate monthly drawdowns and return max drawdown'''

    msr = pandas.read_csv(trial_path)['Value'].pct_change()
    wealth_index = 1000 * (1 + msr).cumprod()
    prev_peaks = wealth_index.cummax()
    drawdown = (wealth_index - prev_peaks) / prev_peaks

    trial_update = []
    with open(trial_path, 'r', encoding='utf-8') as trial_file:
        for line in csv.reader(trial_file):
            trial_update.append(line)

    i = 0
    with open(trial_path, 'w', encoding='utf-8', newline='') as trial_file:
        for line in trial_update:
            try:
                if i == 0:
                    line.append('Drawdown')
                else:
                    line.append(drawdown[i+1] * 100)
                csv.writer(trial_file).writerow(line)
            except (KeyError, ValueError):
                pass
            i += 1

    drawdowns, values = [], []

    with open(trial_path, 'r', encoding='utf-8') as trial_file:
        for line in csv.reader(trial_file):
            try:
                drawdowns.append(float(line[6]))
                values.append(float(line[2]))
            except ValueError:
                pass

    max_dd = min(drawdowns)
    values = values[drawdowns.index(max_dd):]

    ttr = 0
    for value in values:
        if ttr != 0 and value >= values[0]:
            break
        ttr += 1

    return max_dd, ttr

def get_trial_data(output_dir, trial):
    '''Get last value, all-time-high drawdown, max drawdown, and time to recovery'''

    trial_path = get_trial_path(output_dir, trial)

    with open(trial_path, 'rb') as trial_file:
        try:
            trial_file.seek(-2, os.SEEK_END)
            while trial_file.read(1) != b'\n':
                trial_file.seek(-2, os.SEEK_CUR)
        except OSError:
            trial_file.seek(0)

        last_value = trial_file.readline().decode().split(',')[2]

    with open(trial_path, 'r', encoding='utf-8') as trial_file:
        values = []
        for line in csv.reader(trial_file):
            try:
                values.append(float(line[2]))
            except ValueError:
                pass

    values_ath = values[values.index(max(values)):]
    ath_drawdown = 0 - (100 - (min(values_ath) * 100 / max(values_ath)))

    max_drawdown, ttr = get_drawdown(trial_path)

    return last_value, ath_drawdown, max_drawdown, ttr

def mapper(output_dir, trial, inv_total, ranges, mp_ls):
    '''Append results to mapper'''

    mapper_path = os.path.join(output_dir, 'mapper.csv')

    last_value, ath_dd, max_dd, ttr = get_trial_data(output_dir, trial)

    if not os.path.exists(mapper_path):
        with open(mapper_path, 'a', encoding='utf-8') as map_file:
            csv_mapper = csv.writer(map_file,delimiter=',')
            csv_mapper.writerow(header)

    if isinstance(trial, int):
        gain = (float(last_value) * 100 / inv_total) - 100

    with open(mapper_path, 'a', encoding='utf-8') as map_file:
        map_file = csv.writer(map_file,delimiter=',')
        map_file.writerow([trial, last_value, inv_total, gain, ath_dd, max_dd, ttr, ranges, mp_ls])

def run_dca_analysis(output_dir, data):
    '''Run DCA analysis from input data'''

    shares, inv_total, avg_nav = 0, 0, 0

    with open(get_trial_path(output_dir, 0), 'w', encoding='utf-8') as results:
        csv_res = csv.writer(results, delimiter=',')
        csv_res.writerow(['Close', 'Shares', 'Value', 'Inv Monthly', 'Invested Tot', 'Avg NAV'])

        for close in data['Close']:
            inv_monthly = 100
            inv_total += inv_monthly
            shares += inv_monthly / close
            avg_nav = inv_total / shares
            value = shares * close

            csv_res.writerow([close, shares, value, inv_monthly, inv_total, avg_nav])

    mapper(output_dir, 0, inv_total, 0, 0)

def generate_ranges_random():
    '''Generate random ranges'''

    args = parse_arguments()

    ranges = {}
    range_upper_old = None

    if args.force_neg:
        upper_limit_neg = 0
    else:
        upper_limit_neg = 15

    for tier in tiers:

        if tier[5] == 'n':
            upper_limit = upper_limit_neg
        else:
            upper_limit = 15

        if range_upper_old is None:
            range_lower = 9999
            range_upper = round(random.uniform(-15, upper_limit), 1)
            range_upper_old = range_upper
        else:
            range_lower = range_upper_old
            range_upper = round(random.uniform(range_lower, upper_limit), 1)
            range_upper_old = range_upper

        if tier == 'tier_p3':
            range_upper = 9999

        ranges[tier] = [range_lower, range_upper]

    return ranges

def generate_ranges_incremental(i):
    '''Generate incremental ranges'''

    ranges = {}

    for tier in tiers:
        if tier == 'tier_00':
            range_lower = -i
            range_upper = i
        elif tier[6] == '1':
            range_lower = i
            range_upper = i + 2.5
        elif tier[6] == '2':
            range_lower = i + 2.5
            range_upper = i + 5
        elif tier[6] == '3':
            range_lower = i + 5
            range_upper = 9999

        if tier[5] == 'n':
            range_lower, range_upper = 0 - range_upper, 0 - range_lower

        ranges[tier] = [range_lower, range_upper]

    return ranges

async def run_va_analysis(output_dir, trial, data, multipliers, ranges=None):
    '''Run by-range value-averaging analysis from input data'''

    if not multipliers:
        multipliers = gen_multipliers()

    if not ranges:
        ranges = generate_ranges_random()

    with open(get_trial_path(output_dir, trial), 'w', encoding='utf-8') as res:
        csv_res = csv.writer(res, delimiter=',')
        csv_res.writerow(['Close', 'Shares', 'Value', 'Inv Monthly', 'Invested Tot', 'Avg NAV'])

        shares, inv_total, avg_nav = 0, 0, 0

        for close in data['Close']:
            try:
                delta = ((close - avg_nav) * 100) / avg_nav
            except ZeroDivisionError:
                delta = 0

            multiplier = get_multiplier(delta, multipliers, ranges)

            inv_monthly = 100 * multiplier
            inv_total += inv_monthly
            shares += inv_monthly / close
            avg_nav = inv_total / shares
            value = shares * close

            csv_res.writerow([close, shares, value, inv_monthly, inv_total, avg_nav])

    mapper(output_dir, trial, inv_total, ranges, multipliers)

def print_res(str_1, str_2, str_3, str_4='', mes=''):
    '''Print results in table format'''

    def space_1(string):
        return ' ' * (25 - len(str(string)))

    def space_2(string):
        return ' ' * (20 - len(str(string)) - len(mes) + 1)

    args = parse_arguments()

    if mes:
        str_3 = f'[#{str_3}]'

    if not args.quiet:
        print(str_1, space_1(str_1), str_2, mes, space_2(str_2), str_3, str_4, mes)

def get_results(output_dir):
    '''Process, save, and show best results'''

    best_value = best_gain = best_ath_dd = best_max_dd = best_ttr = None

    with open(os.path.join(output_dir, 'mapper.csv'), 'r', encoding='utf-8') as map_file:
        for line in csv.reader(map_file):
            try:
                if int(line[0]) == 0:
                    dca = line
                else:
                    if best_value is None or float(line[1]) >= best_value:
                        best_value = round(float(line[1]), 2)
                        value_line = line

                    if best_gain is None or float(line[3]) >= best_gain:
                        best_gain = round(float(line[3]), 2)
                        gain_line = line

                    if best_ath_dd is None or float(line[4]) <= best_ath_dd:
                        best_ath_dd = round(float(line[4]), 2)
                        ath_dd_line = line

                    if best_max_dd is None or float(line[5]) <= best_max_dd:
                        best_max_dd = round(float(line[5]), 2)
                        max_dd_line = line

                    if best_ttr is None or float(line[6]) <= best_ttr:
                        best_ttr = int(line[6])
                        ttr_line = line
            except ValueError:
                pass

    with open(os.path.join(output_dir, 'best_results.csv'), 'a', encoding='utf-8') as results:
        results = csv.writer(results, delimiter=',')
        results.writerow(header)
        results.writerow(dca)
        results.writerow(value_line)
        results.writerow(gain_line)
        results.writerow(ath_dd_line)
        results.writerow(max_dd_line)
        results.writerow(ttr_line)

    print_res('<stat>', '<dca>', '<smart dca trial>')
    print_res('Value', round(float(dca[1]), 2), value_line[0], best_value, '$')
    print_res('Gain', int(float(dca[3])), gain_line[0], best_gain, '%')
    print_res('All-time-high drawdown', round(float(dca[4]), 2), ath_dd_line[0], best_ath_dd, '%')
    print_res('Max drawdown ', round(float(dca[5]), 2), max_dd_line[0], best_max_dd, '%')
    print_res('Time to recovery', int(dca[6]), ttr_line[0], best_ttr, 'months')

def main():
    '''Main function'''

    args = parse_arguments()

    run_checks()

    start_time = time.monotonic()

    asset = get_asset()

    output_dir = get_output_dir(asset)

    if not os.path.isdir(output_dir):
        os.makedirs(os.path.join(output_dir, 'trials'))

    dl_start = time.monotonic()
    start_date, data = get_data(asset, output_dir)
    dl_end = time.monotonic()

    run_dca_analysis(output_dir, data)

    analysis_start = time.monotonic()
    trial = 1

    if not args.rand_mult:
        mult_ls = gen_multipliers()
    else:
        mult_ls = None

    if not args.incr_ranges:
        if args.trials:
            max_trials = args.trials
        else:
            max_trials = 10000

        while trial <= max_trials:
            asyncio.run(run_va_analysis(output_dir, trial, data, mult_ls))
            trial += 1
    else:
        i = 0
        while i <= 10:
            ranges = generate_ranges_incremental(i)
            asyncio.run(run_va_analysis(output_dir, trial, data, mult_ls, ranges=ranges))
            i += 0.5
            trial += 1
    analysis_end = time.monotonic()

    if not args.quiet:
        print(f'Asset:      {asset}')
        print(f'Start date: {start_date}\n')

    get_results(output_dir)

    if args.time:
        print('\n' + '-' * 75)
        print(f'Download time: {datetime.timedelta(seconds=dl_end-dl_start)}')
        print(f'Analysis time:  {datetime.timedelta(seconds=analysis_end-analysis_start)}')
        print(f'Total execution time: {datetime.timedelta(seconds=time.monotonic()-start_time)}')

if __name__ == '__main__':
    main()
