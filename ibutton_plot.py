#! /usr/bin/env python

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil import parser
import timelib

def parse_dict(f):
    d = {}
    for x in xrange(13):
        line = f.next()  
        k, v = line.strip().replace('? ',': ').split(': ')
        d[k.strip()] = v.strip()
    return d

def parse_val(f):
    skip_nl = 1
    #skip_nl = 13
    dtype=[('date','object'),('unit','S1'),('Temp','f')]
    #datetime in dtype, or convert from string?
    #Shouldn't need to skip metadata if given the same file handle
    T = np.genfromtxt(f, delimiter=',', dtype=dtype, skip_header=skip_nl, names=True)
    #Extract header
    #Extract datetime properly
    #import pandas as pd
    #frame=pd.read_table('/tmp/gist', header=None, skiprows=22,delimiter='\s+') 
    T['DateTime'] = [parser.parse(i) for i in T['DateTime']] 
    return T

def reconstruct(T):
    #T = T[::3]
    t_samp = timelib.dt2o(T['DateTime'])
    min_t = t_samp.min()
    max_t = t_samp.max()
    #Max signal frequency is daily
    #fs = 1.0/3
    dt_samp = 1.0/6
    #dt_samp = 1.0/2
    #hourly interpolation
    dt_interp = 1.0/12.0 
    t_interp = np.arange(min_t, max_t+dt_interp, dt_interp)
    #t = np.arange(min_t, max_t+dt_interp, dt_interp)
    n_coeff = T['Value'].shape[0]

    #T_interp = 0 
    #for k in range(0, n_coeff):
    #    T_interp += T['Value'][k]*np.sinc(np.pi*(k-fs*t_interp))
    
    T_interp = 0
    for k in range(0, n_coeff):
       T_interp += T['Value'][k]*np.sinc(np.pi*(t_interp - t_samp[k])/dt_samp) 

    return timelib.o2dt(t_interp), T_interp

fnlist = sys.argv[1:]

fig = plt.figure(figsize=(10,7.5))

T_list = []

for fn in fnlist:
    f = open(fn, 'r')
    #import pdb; pdb.set_trace()
    d = parse_dict(f)
    T = parse_val(f)
    f.close()
    T_list.append(T['Value'])
    lbl = os.path.splitext(fn)[0].split('_trim')[0]
    #plt.plot(T['DateTime'], T['Value'], label='%s (%s)' % (lbl, d['1-Wire/iButton Registration Number']))
    plt.plot(T['DateTime'], T['Value'], label=lbl)
    #t_interp, T_interp = reconstruct(T)
    #plt.plot(t_interp, T_interp) 

plt.title('2013/2014 NLBS iButton Temperature Record')
plt.ylabel('Temperature (C)')
#plt.xlabel('DateTime')
plt.axhline(0,color='k',linestyle='--')
plt.legend(loc=3, prop={'size':8})
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('ibutton_timeseries.ps', orientation='landscape')

fig = plt.figure(figsize=(10,7.5))
T_list = np.array(T_list)
T_plot = T_list[:,::10]
T_plot = T_list
num_plots = T_plot.shape[1] 

# Have a look at the colormaps here and decide which one you'd like:
# http://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html
colormap = plt.cm.gist_rainbow_r
ax = plt.gca()
ax.set_color_cycle([colormap(i) for i in np.linspace(0, 1.0, num_plots)])

z = [1.65, 0, -1.0, -1.5]
lineobj = plt.plot(T_plot, z, marker='o')
plt.axvline(0,color='k',linestyle='--')
plt.axhline(0,color='k',linestyle='-')
plt.xlabel('Temperature (C)')
plt.ylabel('Depth (m)')
plt.xlim(-40, 10)
plt.ylim(-2.0, 2.0)
plt.title('2013/2014 NLBS iButton Temperature vs. Depth')
plt.tight_layout()

#handles, labels = ax.get_legend_handles_labels()
plt.legend(lineobj[::200],T['DateTime'][::200], prop={'size':8}, loc='5')
plt.savefig('ibutton_T_vs_depth.ps', orientation='landscape')

plt.show()

