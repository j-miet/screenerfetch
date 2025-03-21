"""Data plotting functions for custom workbooks.

Data is read from current workbook - make sure one exists in 'workbooks' folder.

These functions only work for current custom query, unless yours happens to share similar columns. Currently, it means you need the following column names & my_query columns:  
________________________________________________   
header = your custom query headers (also your workbook headers)  
my_query column =  actual TradingView API column value; value is wrapped in parethesis - don't include those, just the 
    string inside.

_________________________  
'Date'  (nothing, not part of my_query - will always be first column, automatically)  
'Symbol' ('name')  
'Low' ('low')  
'High' ('high')  
'Price' ('close')  
'Open' ('open')  
'Float' ('float_shares_outstanding_current')  
'Volume' ('volume' )  
'Market Cap' ('market_cap_basic')  
'Pre-market Open' ('premarket_open')  
'Chg from Open %' ('change_from_open')
"""

from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from paths import FilePaths

# matplotlib generates plenty of type errors for smallest possible things; they are ignored.
# mypy: ignore-errors

# Style values https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html
STYLE = 'dark_background'

def show_daily_average_candles() -> None:
    """Display daily average candle of all symbols.
    
    A daily average candle values are calculated by taking average on each of them (low, high, open, close) over all 
    symbols that day.
    """
    plt.style.use(STYLE)
    cs_pos_color = 'green'
    cs_neg_color = 'red'
    cs_width = 0.03
    cs_body_width = 0.3

    df = pd.read_excel(FilePaths.wb_path, 0, header=0, usecols=['Date', 'Low', 'High', 'Price', 'Open'])
    # read_excel orders columns based on their sheet order: currently, columns are ordered Open < Price < Low < High. 
    # So line below re-arranges columns to a order that aligns with the rest of code: Low < High < Price < Open.
    df = df[['Date', 'Low', 'High', 'Price', 'Open']] 
    df['Date'] = df['Date'].apply(lambda x: str(x).replace(' 00:00:00', '')) #normalize datetime object values.
    dates = df['Date'].unique()
    # sets a minimum height for candle bodies, especially helpful if Open=Price; naturally skews the actual values a 
    #bit, but helps with visual clarity.
    delta = 0.001*df['High'].max(numeric_only=True)

    fig = plt.figure()
    ax_candles = fig.add_subplot(3, 1, (1,2))
    ax_counts = fig.add_subplot(3, 1, 3)
    AverageCandles = namedtuple('AverageCandles', ['low', 'high', 'price', 'open'])
    for d in dates:
        avg_list = list(df.loc[df['Date'] == d].mean(axis=0, numeric_only=True).values)
        for index in range(len(avg_list)):
            avg_list[index] = round(float(avg_list[index]), 2)
        
        candle_averages = AverageCandles(avg_list[0], avg_list[1], avg_list[2], avg_list[3])
        if candle_averages.price > candle_averages.open:
            ax_candles.bar(d, candle_averages.high+delta-candle_averages.price, cs_width, 
                           candle_averages.price, color=cs_pos_color)
            ax_candles.bar(d, candle_averages.price+delta-candle_averages.open, cs_body_width, 
                           candle_averages.open, color=cs_pos_color)
            ax_candles.bar(d, candle_averages.open+delta-candle_averages.low, cs_width, 
                           candle_averages.low, color=cs_pos_color)
        else:
            ax_candles.bar(d, candle_averages.high+delta-candle_averages.open, cs_width, 
                           candle_averages.open, color=cs_neg_color)
            ax_candles.bar(d, candle_averages.open+delta-candle_averages.price, cs_body_width,
                           candle_averages.price, color=cs_neg_color)
            ax_candles.bar(d, candle_averages.price+delta-candle_averages.low, cs_width,
                            candle_averages.low, color=cs_neg_color)

    font_x= {'family':'serif','color':'cornflowerblue','size':14}
    font_y = {'family':'serif','color':'cornflowerblue','size':14}
    ax_candles.set_title('Daily average candles\n= low, high, close and open of a candle are each obtained by taking '+
                         'the arithmetic mean over the corresponding values of all symbols that day')
    ax_candles.set_xlabel('Dates', fontdict=font_x)
    ax_candles.set_ylabel('Price', fontdict=font_y)
    ax_candles.set_axisbelow(True)
    ax_candles.set_ylim(bottom=0, top=max([df['High'].loc[df['Date'] == val].mean() for val in dates])+1)
    ax_candles.xaxis.set_major_locator(plt.MaxNLocator(steps=[2,3,4]))
    ax_candles.yaxis.grid(color='gray', linestyle='--')
    ax_candles.xaxis.grid(color='gray', linestyle='--')
    
    ax_counts.set_title('Total amount of symbols each day')
    ax_counts.set_xlabel('Dates', fontdict=font_x)
    ax_counts.set_ylabel('Symbol count', fontdict=font_y)
    ax_counts.xaxis.set_major_locator(plt.MaxNLocator(steps=[2,3,4]))
    symbol_count = []
    for val in dates:
        symbol_count.append(df.loc[df['Date'] == val]['Date'].count())
    
    ax_counts.plot(dates, symbol_count)
    ax_counts_pos = ax_counts.get_position()
    ax_counts_pos.y0, ax_counts_pos.y1 = ax_counts_pos.y0-0.05, ax_counts_pos.y1-0.05
    ax_counts.set_position(ax_counts_pos)
    plt.show()

def show_average_lines() -> None:
    """Displays daily averages and draws them as separate lines.
     
    Values tracked are premarket open, open and close. Average is then calculated for each of these 
    values over all symbols of a day, resulting into 3 different lines."""
    plt.style.use(STYLE)
    pre_open_avg = []
    open_avg = []
    close_avg = []

    df = pd.read_excel(FilePaths.wb_path, 0, header=0, usecols=['Date', 'Pre-market Open', 'Open', 
                                                                'Price'])
    df['Date'] = df['Date'].apply(lambda x: str(x).replace(' 00:00:00', ''))
    dates = df['Date'].unique()
    for val in dates:
        temp_df: pd.DataFrame = df.loc[df['Date'] == val]
        avg_list = list(temp_df.mean(axis=0, numeric_only=True).values)
        for index in range(len(avg_list)):
            avg_list[index] = round(float(avg_list[index]), 2)
        pre_open_avg.append(avg_list[0])
        open_avg.append(avg_list[1])
        close_avg.append(avg_list[2])

    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(steps=[2,3,4]))
    plt.title('Averages of pre-market open, open and close')
    plt.plot(dates, pre_open_avg, 'o--', color='lightsteelblue', label='pre-open')
    plt.plot(dates, open_avg, 'o--', color='dodgerblue', label='open')
    plt.plot(dates, close_avg, 'o--', color='goldenrod', label='close')
    plt.legend()
    plt.show()

def show_daily_candles(date: str) -> None:
    """Draws all daily candlesticks for given date.

    Also displays volumes of each symbol + distribution of green and red candles.
    
    Args:
        date: A date string in 'yyyy-mm-dd' format. Sheet data for this date must exists in current workbook.
    """
    plt.style.use(STYLE)
    cs_pos_color = 'green'
    cs_neg_color = 'red'
    cs_width = 0.05
    cs_body_width = 0.5

    df = pd.read_excel(FilePaths.wb_path, 0, header=0, usecols=['Date', 'Symbol', 'Open', 'Low', 'High', 'Price', 
                                                                'Volume'])
    df['Date'] = df['Date'].apply(lambda x: str(x).replace(' 00:00:00', ''))
    df = df.loc[df['Date'] == date]
    df = df.reset_index(drop=True)
   
    delta = 0.001*df['High'].max(numeric_only=True)

    fig = plt.figure()
    ax = fig.add_subplot()
    font_x= {'family':'serif','color':'cornflowerblue','size':14}
    font_y = {'family':'serif','color':'cornflowerblue','size':14}
    ax.set_title(f'{date} daily candles.\n Includes volumes, highest/lowest price point of the day, and the '+
                  'distribution of green and red candles')
    ax.set_xlabel('Symbols', fontdict=font_x)
    ax.set_ylabel('Price', fontdict=font_y)
    ax.set_ylim(bottom=0, auto=True)
    ax.yaxis.grid(color='gray', linestyle=':')
    ax.locator_params(axis='y', nbins=20)
    plt.xticks(rotation=60, ha='right')
    for row_index in range(len(df)):
        cs_df = df.loc[row_index]
        name = cs_df['Symbol']
        if cs_df['Price'] > cs_df['Open']:
            plt.bar(name, cs_df['High']+delta-cs_df['Price'], cs_width, cs_df['Price'], color=cs_pos_color)
            plt.bar(name, cs_df['Price']+delta-cs_df['Open'], cs_body_width, cs_df['Open'], color=cs_pos_color)
            plt.bar(name, cs_df['Open']+delta-cs_df['Low'], cs_width, cs_df['Low'], color=cs_pos_color, 
                    label=name+': '+str(cs_df['Volume']))
        else:
            plt.bar(name, cs_df['High']+delta-cs_df['Open'], cs_width, cs_df['Open'], color=cs_neg_color)
            plt.bar(name, cs_df['Open']+delta-cs_df['Price'], cs_body_width, cs_df['Price'], color=cs_neg_color)
            plt.bar(name, cs_df['Price']+delta-cs_df['Low'], cs_width, cs_df['Low'], color=cs_neg_color,
                    label=name+': '+str(cs_df['Volume']))
            
    daily_max = df['High'].max()
    daily_max_name = df[['Symbol', 'High']].loc[df['High'] == daily_max].iat[0,0]
    daily_min = df['Low'].min()
    daily_min_name = df[['Symbol', 'Low']].loc[df['Low'] == daily_min].iat[0,0]
    green_total = df[df['Price'] - df['Open'] > 0]['Price'].count()
    red_total = df['Price'].count()-green_total
    green_pct = f"{(green_total/(green_total+red_total)*100):.2f}"
    red_pct = f"{(red_total/(green_total+red_total)*100):.2f}"

    ax = plt.gca()
    vol_legend = ax.legend(title='Volume', loc='upper left', bbox_to_anchor=(1, 1.125), facecolor='darkslategray')
    plt.legend(title=f'Highest: {daily_max} ({daily_max_name})\nLowest: {daily_min} ({daily_min_name})'
               f'\nGreen: {green_total} ({green_pct}%)\nRed: {red_total} ({red_pct}%)', 
               loc='upper right', facecolor='darkslategray', ncols=2, labels='', title_fontsize=11,
               bbox_to_anchor=(1.005, 1.125))
    plt.setp(plt.gca().get_legend().get_title(), color='azure')
    ax.add_artist(vol_legend)
    plt.show()

def show_distributions() -> None:
    """Frequency distributions created from workbook data."""
    plt.style.use(STYLE)

    df = pd.read_excel(FilePaths.wb_path, 0, header=0, 
                       usecols=['Open', 'High', 'Chg from Open %', 'Float', 'Market Cap'])
    df['High-to-Open %'] = ((df['High']/df['Open'])-1)*100

    df_mc = df['Market Cap'].loc[df['Market Cap'] != '-']
    df_f = df['Float'].loc[df['Float'] != '-']
    df_cfo = df['Chg from Open %']
    
    market_caps = {'nano': int(df_mc.loc[df_mc < 5e7].count()),
                   'micro': int(df_mc.loc[(df_mc >= 5e7) & (df_mc <= 2.5e8)].count()),
                   'small': int(df_mc.loc[df_mc >= 2.5e8].count())}
    floats = {'low': int(df_f.loc[df_f < 1e7].count()),
              'mid': int(df_f.loc[(df_f >= 1e7) & (df_f < 1e8)].count()),
              'high': int(df_f.loc[df_f >= 1e8].count())}
    change_percents = {'<-20': int(df_cfo.loc[df_cfo < 20].count()),
                      '[-20, -10]': int(df_cfo.loc[(df_cfo >= -20) & (df_cfo <= -10)].count()),
                      '(-10, -1)': int(df_cfo.loc[(df_cfo >= -10) & (df_cfo < 0)].count()),
                      '[-1, 1]': int(df_cfo.loc[(df_cfo >= -1) & (df_cfo <= 1)].count()),
                      '(1, 10)': int(df_cfo.loc[(df_cfo >= 0) & (df_cfo < 10)].count()),
                      '[10, 20]': int(df_cfo.loc[(df_cfo >= 10) & (df_cfo <= 20)].count()),
                      '>20': int(df_cfo.loc[df_cfo > 20].count())}
    market_caps_labels = ['nano - 0-50M', 'micro - 50M-250M', 'small - >250M']
    floats_labels = ['low - 0-10M', 'mid - 10M-100M', 'high - >100M']

    def val_and_percent(pct_val: float, allvals: float) -> str:
        # https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_and_donut_labels.html#sphx-glr-gallery-pie-and-polar-charts-pie-and-donut-labels-py
        actual_val = int(np.round(pct_val/100.*np.sum(allvals)))
        return f"{pct_val:.1f}%\n({actual_val})"

    fig = plt.figure()
    fig.suptitle('Frequency distributions\nSymbols with invalid ' 
                 'data such as missing float/market cap are not counted')
    ax_hist1 = fig.add_subplot(2, 3, (1, 4))
    ax_hist2 = fig.add_subplot(2, 3, 2)
    ax_pie1 = fig.add_subplot(2, 3, 5)
    ax_pie2 = fig.add_subplot(2, 3, 3)
    ax_pie3 = fig.add_subplot(2, 3, 6)

    font_x= {'family':'serif','color':'cornflowerblue','size':14}
    font_y = {'family':'serif','color':'cornflowerblue','size':14}
    ax_hist1.set_facecolor('gainsboro')
    ax_hist1.set_title('Frequency of High-to-Open % values')
    ax_hist1.set_xlabel('High-to-Open % = ((High price/Open price)-1)*100)', fontdict=font_x)
    ax_hist1.set_ylabel('Frequency (log base 2)', fontdict=font_y)
    # if histogram values are way too high, consider logarithmic scale
    ax_hist1.set_yscale('log', base=2)
    ax_hist1.locator_params(axis='x', nbins=10)
    df['High-to-Open %'].hist(ax=ax_hist1, bins=30, grid=False, edgecolor='black', color='lightblue',
                              label=f'Highest: {df['High-to-Open %'].max(numeric_only=True):.2f} %')
    ax_hist1.legend(facecolor='grey')

    ax_hist2.set_facecolor('gainsboro')
    ax_hist2.set_title('Frequency of Chg from Open % values\n (+ a pie chart version of same data)')
    ax_hist2.set_xlabel('Chg from Open % = ((Close price/Open price)-1)*100', fontdict=font_x)
    ax_hist2.set_ylabel('Frequency (log base 2)', fontdict=font_y)
    ax_hist2.set_yscale('log', base=2)
    df['Chg from Open %'].hist(ax=ax_hist2, bins=30, grid=False, edgecolor='black',
                               label=f'Highest: {df['Chg from Open %'].max(numeric_only=True):.2f} % \n'+
                                f'Lowest: {df['Chg from Open %'].min(numeric_only=True):.2f} %')
    ax_hist2.legend(facecolor='grey')

    ax_pie1.pie([val for val in change_percents.values()], labels=change_percents.keys(), labeldistance=None,
             colors=['red', 'orangered', 'orange', 'gray', 'yellowgreen', 'lightgreen', 'limegreen'], 
             textprops=dict(color='ghostwhite'), 
             autopct=lambda x: val_and_percent(x, [val for val in change_percents.values()]), pctdistance=0.85)
    ax_pie2.pie([val for val in market_caps.values()], labels=market_caps.keys(), labeldistance=None,
             colors=['coral', 'dodgerblue', 'limegreen'], textprops=dict(color='ghostwhite'), 
             autopct=lambda x: val_and_percent(x, [val for val in market_caps.values()]), pctdistance=0.85)
    ax_pie2.set_title('Market caps')
    ax_pie3.pie([val for val in floats.values()], labels=floats.keys(), labeldistance=None,
             colors=['coral', 'dodgerblue', 'limegreen'], textprops=dict(color='ghostwhite'),
             autopct=lambda x: val_and_percent(x, [val for val in floats.values()]), pctdistance=0.85)
    ax_pie3.set_title('Share floats')

    rect = plt.Rectangle((0.36, 0.11), 0.3, 0.77, fill=False, color="dimgray", lw=2, zorder=1000, 
                         transform=fig.transFigure, figure=fig)
    fig.patches.extend([rect])
    hist2_pos = ax_hist2.get_position()
    hist2_pos.y0, hist2_pos.y1 = hist2_pos.y0-0.05, hist2_pos.y1-0.05
    ax_hist2.set_position(hist2_pos)
    pie1_pos = ax_pie1.get_position()
    pie1_pos.y0, pie1_pos.y1 = pie1_pos.y0-0.04, pie1_pos.y1-0.04
    ax_pie1.set_position(pie1_pos)

    ax_pie1.legend(loc='upper right', bbox_to_anchor=(1.35, 0.95))
    ax_pie2.legend(loc='upper right', labels=market_caps_labels, bbox_to_anchor=(1.4, 1))
    ax_pie3.legend(loc='upper right', labels=floats_labels, bbox_to_anchor=(1.35, 1))
    plt.show()

def show_high_to_open_vs_float_and_mc() -> None:
    """Displays how float and market cap are correlated to high intraday moves.
    
    Measure of high moves is ((high-open)-1)*100 i.e. how much higher has price reached compared to open.
    """
    plt.style.use(STYLE)

    df = pd.read_excel(FilePaths.wb_path, 0, header=0, usecols=['Open', 'High', 'Float', 'Market Cap'])
    df['High-to-Open %'] = ((df['High']/df['Open'])-1)*100
    df = df[['Float', 'High-to-Open %', 'Market Cap']].loc[(df['Float'] != '-') & (df['Market Cap'] != '-')]

    font_x= {'family':'serif','color':'cornflowerblue','size':14}
    font_y = {'family':'serif','color':'cornflowerblue','size':14}
    plt.title('Correlation between float/market cap and High-to-Open % values\n'
              'High-to-Open % = ((High price/Open price)-1)*100')
    plt.xlabel('High-to-Open %', fontdict=font_x)
    plt.ylabel('Float / Market Cap (log10)', fontdict=font_y)
    plt.locator_params(axis='x', nbins=20)
    plt.ticklabel_format(style='plain', useOffset=False)
    plt.axhline(y=1e7, color='gray', linestyle=':', label='10M threshold')
    plt.yscale('log')

    x = df['High-to-Open %'].astype('float')
    y1 = df['Float'].astype('float')
    y2 = df['Market Cap'].astype('float')
    plt.scatter(x, y1, 12, color='deepskyblue', label='Float')
    plt.scatter(x, y2, 12, color='gold', label='Market Cap')

    plt.xlim(xmin=0.0)
    plt.legend()
    plt.show()