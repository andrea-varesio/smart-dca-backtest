# Smart Dollar Cost Averaging backtest

## Requirements
- Install Python requirements with `pip3 install -r requirements.txt`

Note: this program has only been tested on Linux.

## Usage
```
main.py [-h] [-l] [-d] [-v] [-u] [-a ASSET | --sp500 | --dji | --nasdaq | --nyse | --r2000 | --ftse100 | --n225 | --ftsemib] [-p PERIOD] [-M MAX_MULT] [-m MIN_MULT] [-fM] [-fm] [-mi MULT_INCR | -rm] [-fn] [-t TRIALS | -ir] [-O OUTPUT] [-q] [-T]
```

Short | Argument | Info
---|---|---
`-h` | `--help` | show this help message and exit
`-l` | `--license` | show license
`-d` | `--disclaimer` | show disclaimer
`-v` | `--version` | show current version
`-u` | `--update` | find new versions and update
`-a` | `--asset` | asset to analyze [Default: SWDA.MI]
` ` | `--sp500` | S&P 500 (avail: 1927) [^GSPC]
` ` | `--dji` | DJI (avail: 1992) [^DJI]
` ` | `--nasdaq` | NASDAQ Composite (avail: 1971) [^IXIC]
` ` | `--nyse` | NYSE Composite (avail: 1965) [^NYA]
` ` | `--r2000` | Russell 2000 (avail: 1987) [^RUT]
` ` | `--ftse100` | FTSE 100 (avail: 1984) [^FTSE]
` ` | `--n225` | Nikkei 225 (avail: 1965) [^N225]
` ` | `--ftsemib` | FTSE MIB (avail: 1997) [FTSEMIB.MI]
`-p` | `--period` | years to backtest [Default: ALL]
`-M` | `--max-mult` | maximum multiplier [Default: 2]
`-m` | `--min-mult` | minimum multiplier [Default: 0.25]
`-fM` | `--force-max` | force max multiplier limit
`-fm` | `--force-min` | force min multiplier limit
`-mi` | `--mult-incr` | multiplier increment [Default: 0.25]
`-rm` | `--rand-mult` | generate random multipliers
`-fn` | `--force-neg` | force values < 0 for negative ranges
`-t` | `--trials` | random ranges trials [Default: 10000]
`-i` | `--incr-ranges` | use incremental ranges instead of random
`-O` | `--output` | path to output directory
`-q` | `--quiet` | disable verbosity
`-T` | `--time` | measure script execution time

## Asset
The default asset is SWDA.MI: iShares Core MSCI World UCITS ETF USD (Acc).

This can easily be changed with the parameter `-a` or `--asset` followed by the ticker of the security, as listed on [Yahoo Finance](https://finance.yahoo.com/).
You also have the option to use other built-in assets, such as the S&P 500 index (`--sp500`). The complete list can be found in the **Usage** paragraph.

## Multipliers
Smart DCA takes different ranges in which the average asset price falls in, depending on which a different multiplier for the monthly investment is assigned to the corresponding tier.

By default, the set of multipliers is the same for each trial and is generated with increments (by default the increment is 0.25, this can be customized with `-mi` or `--mult-incr`).
The program offers the ability to generate a random set of multiplier for each trial (there is however a ~3% performance hit on total time). This can be achieved by passing the `-rm` or `--rand-mult` parameter.

You can specify the maximum (`-M`, `--max-mult`) and minimum (`-m`, `--min-mult`) multipliers. You can also decide whether or not these boundries are used as limits or actual multipliers, with `-fM`, `--force-max`, and `-fm`, `--force-min`.

## Ranges
The default behavior of this program is to generate an array of 7 tiers with a random range (which falls between -15% and 15%) each, with the `n` (negative) tiers being the ones that have a range assigned that is less than the average investment price. 

However, given that the ranges are randomly generated, it may occur that some are greater than zero, despite the tier. To force the use of negative ranges in negative tiers, you can pass the `-fn` or `--force-neg` parameter.

You also have the option to generate incremental ranges with the `-ir` or `--incr-ranges` parameter. This option will generate 21 combinations of ranges

### Example:

Tier | Ranges (incremental: range 21) | Multiplier (default)
---|---|---
n3 | avg < -15% | 1.75
n2 | -15.0% < avg < -12.5% | 1.5
n1 | -12.5% < avg < -10.0% | 1.25
00 | -10.0% < avg < 10.0% | 1.00
p1 | 10.0% < avg < 12.5% | 0.75
p2 | 12.5 < avg < 15.0% | 0.5
p3 | 15.0% < avg | 0.25

## Updating
The recommended way to update is by cloning the repository, as all the commits are signed with my key.

However, if you prefer, you can also run the program with the `-u` or `--update` parameter to perform an automatic update:

The script will check the updated sha512sum published in `main.py.DIGESTS.asc` and compare it with the hash of the updated version of the program. If it matches, the program will update itself, otherwise the process will stop.

You also have the option to verify the signature of `main.py.DIGESTS.asc` to ensure all the hashes are genuine.

## Contributions
Contributions are welcome, feel free to submit issues and/or pull requests.

Especially looking for optimizations and new ideas/features.

### To-Do
- multi-asset evaluations
- multi-year drawdowns
- consider keeping data in memory and only saving on request
- stats
- graphs

## Disclaimer

By using this project, you hereby consent to this disclaimer and agree to its terms.

- This project or its content are NOT to be considered as investment advice.
- I’m NOT a financial advisor.
- The analysis produced by this project does not guarantee any specific result or profit.
- The analysis produced by this project has NO proven rate of accuracy, and past performance does NOT indicate future results.
- Do NOT trade or invest based upon the analysis presented by this project.
- Always do your own research and only invest solely based on your own findings and personal judgment after consulting with a professional/licensed financial advisor.
- Trading and investing is extremely high risk and may result in partial or total loss of your capital.
- The material on this project has NO regard to any specific investment objectives, financial situation, or particular needs of any user.
- This project is presented solely for informational and entertainment purposes and is NOT to be construed as a recommendation, solicitation,
or an offer to buy or sell, long or short any securities, commodities, cryptocurrencies, or any related financial instruments.

I shall NOT be held liable for any of your personal trading/investing decisions and/or loss/damage of any kind arising out of the use of all or any part of the material presented in this project.

## LICENSE
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

"Smart DCA backtest" - Smart Dollar Cost Averaging backtest<br />
Copyright (C) 2022 Andrea Varesio <https://www.andreavaresio.com/>.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a [copy of the GNU General Public License](https://github.com/andrea-varesio/smart-dca-backtest/blob/main/LICENSE)
along with this program.  If not, see <https://www.gnu.org/licenses/>.

<div align="center">
<a href="https://github.com/andrea-varesio/smart-dca-backtest/">
  <img src="http://hits.dwyl.com/andrea-varesio/smart-dca-backtest.svg?style=flat-square" alt="Hit count" />
</a>
</div>