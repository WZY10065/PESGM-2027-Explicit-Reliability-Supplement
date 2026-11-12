"""Generate the README topology diagrams from the supplied Excel workbooks.

Requirements: Python 3, matplotlib, numpy, networkx, openpyxl, Pillow.
Run from any directory: python scripts/plot_topologies.py
"""
from pathlib import Path
import hashlib
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np
import openpyxl
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
INK = '#24333F'
CLOSED = '#667782'
OPEN = '#AD5270'
GFM = '#197C9A'
GFL = '#BC792B'
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 12,
    'text.color': INK,
    'svg.fonttype': 'none',
    'pdf.fonttype': 42,
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.transparent': False,
})


def records(workbook, sheet):
    data = list(workbook[sheet].values)
    return [dict(zip(data[0], row)) for row in data[1:] if row[0] is not None]


def load_case(size):
    source = ROOT / f'omra_case_{size}node_data.xlsx'
    workbook = openpyxl.load_workbook(source, data_only=True)
    nodes = records(workbook, 'Nodes')
    branches = records(workbook, 'Branches')
    devices = records(workbook, 'DeviceConfig')
    dg = records(workbook, 'DGConfig')
    settings = {r['parameter']: r['value'] for r in records(workbook, 'Case')}
    endpoints = {(int(r['branch_from']), int(r['branch_to']), int(r['endpoint_node'])): r
                 for r in devices}
    closed = {}
    for r in branches:
        i, j = int(r['branch_from']), int(r['branch_to'])
        closed[(i, j)] = int(all(int(endpoints[(i, j, n)]['normal_status']) for n in (i, j)))
    roles = {int(r['node']): str(r.get('dg_type') or '').upper() for r in dg}
    sources = {int(r['node']) for r in nodes if r['is_source']}
    if size == 10:
        xy = {1:(0,2), 2:(2,2), 3:(4,2), 4:(6,2), 5:(8,2),
              6:(4,0), 7:(6,0), 8:(8,0), 9:(10,0), 10:(12,0)}
    else:
        xy = {int(r['node']):(float(r['layout_x'])/100, -float(r['layout_y'])/100) for r in nodes}
    workbook.close()
    return source, nodes, branches, endpoints, closed, roles, sources, xy, settings


def draw(size):
    source, nodes, branches, endpoints, closed, roles, sources, xy, settings = load_case(size)
    dense = size == 54
    fig = plt.figure(figsize=(12, 10.8 if dense else 4.5))
    ax = fig.add_axes([.055, .19 if dense else .27, .89, .70 if dense else .55])
    graph = nx.Graph()
    graph.add_nodes_from(xy)
    graph.add_edges_from(closed)
    normal = nx.Graph()
    normal.add_nodes_from(xy)
    normal.add_edges_from(e for e, state in closed.items() if state)
    assert nx.is_forest(normal)
    assert all(len(set(c) & sources) == 1 for c in nx.connected_components(normal))
    assert len(xy) == size and len(closed) == (9 if size == 10 else 61)
    assert sum(closed.values()) == (8 if size == 10 else 50)
    if dense:
        assert closed[(27,28)] == 1 and closed[(35,36)] == 0
    else:
        assert closed[(7,8)] == 0

    for edge, state in closed.items():
        i, j = edge
        a, b = np.asarray(xy[i]), np.asarray(xy[j])
        color = CLOSED if state else OPEN
        ax.plot([a[0],b[0]], [a[1],b[1]], color=color, lw=1.8 if dense else 2.1,
                ls='-' if state else (0,(5,3.5)), zorder=1)
        unit = (b-a)/np.linalg.norm(b-a)
        offset = min(.16 if dense else .28, np.linalg.norm(b-a)*.24)
        for n, point, direction in ((i,a,unit),(j,b,-unit)):
            device = endpoints[(i,j,n)]
            cb = device['device_type'] == 'CB'
            p = point + direction*offset
            ax.plot(*p, marker='s' if cb else 'o', ms=(4.2 if cb else 3.5) if dense else (5.5 if cb else 4.8),
                    mec=INK if cb else color, mfc=INK if cb else 'white', mew=1,
                    linestyle='none', zorder=3)

    for n, (x,y) in xy.items():
        role = roles.get(n,'')
        if n in sources: marker, fill, marker_size = 's', INK, 8.8 if dense else 11
        elif role == 'GFM': marker, fill, marker_size = '^', GFM, 11.0 if dense else 13
        elif role == 'GFL': marker, fill, marker_size = 'D', GFL, 9.0 if dense else 11
        else: marker, fill, marker_size = 'o', 'white', 5.2 if dense else 6.2
        ax.plot(x,y,marker=marker,ms=marker_size,mec=INK if fill=='white' else fill,
                mfc=fill,mew=1.25,linestyle='none',zorder=5)
        if dense:
            angles=sorted(math.atan2(xy[j][1]-y,xy[j][0]-x)%(2*math.pi) for j in graph[n])
            gaps=[(((angles[(k+1)%len(angles)]-v)%(2*math.pi)) if len(angles)>1 else 2*math.pi,v)
                  for k,v in enumerate(angles)]
            gap,start=max(gaps); angle=start+gap/2
            dx,dy=7.2*math.cos(angle),7.2*math.sin(angle)
            ha='left' if dx>1.5 else 'right' if dx < -1.5 else 'center'
            va='bottom' if dy>1.5 else 'top' if dy < -1.5 else 'center'
            if n==14:dx,dy,ha,va=7,8,'left','bottom'
        else:
            dx,dy,ha,va=0,-12,'center','top'
            if n==3:dx,dy,ha,va=0,12,'center','bottom'
        ax.annotate(str(n),(x,y),xytext=(dx,dy),textcoords='offset points',ha=ha,va=va,
                    fontsize=11 if dense else 13,zorder=7,
                    path_effects=[pe.withStroke(linewidth=2.8,foreground='white')])
    if not dense:
        for n,label in [(4,'GFM'),(5,'GFL')]:
            ax.annotate(label,xy[n],xytext=(0,17),textcoords='offset points',ha='center',
                        fontsize=11,color=GFM if n==4 else GFL)
        ax.text(7,-.53,'Normally open 7–8',ha='center',fontsize=10,color=OPEN)
    ax.set_aspect('equal')
    xx,yy=zip(*xy.values())
    ax.set_xlim(min(xx)-.65,max(xx)+.65)
    ax.set_ylim(min(yy)-.65,max(yy)+(.65 if dense else .8))
    ax.set_axis_off()
    fig.text(.055,.957,f'{size}-bus distribution network',fontsize=20,fontweight='bold',va='top')
    fig.text(.945,.953,f"{settings['V_base_kV']:g} kV",ha='right',va='top',fontsize=12,color=CLOSED)
    fig.text(.055,.918 if dense else .865,'Reference device configuration · Normal operation',
             fontsize=11,color=CLOSED,va='top')
    handles=[
      Line2D([],[],marker='s',mfc=INK,mec=INK,color='none',ms=8,label='Grid source'),
      Line2D([],[],marker='^',mfc=GFM,mec=GFM,color='none',ms=9,label='GFM inverter'),
      Line2D([],[],marker='D',mfc=GFL,mec=GFL,color='none',ms=8,label='GFL inverter'),
      Line2D([],[],marker='o',mfc='white',mec=INK,color='none',ms=5,label='Load bus'),
      Line2D([],[],color=CLOSED,lw=2,label='Closed branch'),
      Line2D([],[],color=OPEN,lw=2,ls=(0,(5,3.5)),label='Normally open branch'),
      Line2D([],[],marker='s',mfc=INK,mec=INK,color='none',ms=5,label='CB endpoint'),
      Line2D([],[],marker='o',mfc='white',mec=CLOSED,color='none',ms=4.5,label='SW endpoint')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,.088 if dense else .085),
               ncol=4,fontsize=10.2,frameon=False,columnspacing=2,handletextpad=.6,
               handlelength=2,labelspacing=1.05)
    nopen=sum(not v for v in closed.values())
    cb_count=sum(r['device_type']=='CB' for r in endpoints.values())
    sw_count=sum(r['device_type']=='SW' for r in endpoints.values())
    demand=sum(float(r['P_load_MW'] or 0) for r in nodes)
    customers=sum(int(r['customers'] or 0) for r in nodes)
    fig.text(.055,.056,f'{len(xy)} buses  |  {len(closed)} branches  |  {len(sources)} grid sources  |  {nopen} normally open',
             fontsize=9.3,color=CLOSED)
    fig.text(.945,.056,f'{demand:.3f} MW  |  {customers:,} customers  |  {cb_count} CB + {sw_count} SW endpoints',
             ha='right',fontsize=9.3,color=CLOSED)
    fig.text(.055,.021,'Schematic positions. Branch states follow endpoint-device settings.',fontsize=9,color=CLOSED)
    if dense:
        fig.text(.945,.021,'Reference inverter locations are not fixed greenfield investments.',
                 ha='right',fontsize=9,color=CLOSED)
    OUT.mkdir(parents=True,exist_ok=True)
    stem=OUT/f'topology_{size}bus'
    fig.savefig(stem.with_suffix('.svg'))
    svg=stem.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    fig.savefig(stem.with_suffix('.png'),dpi=600)
    plt.close(fig)
    png=Image.open(stem.with_suffix('.png'))
    return {'case':size,'nodes':len(xy),'branches':len(closed),'closed_branches':sum(closed.values()),
            'open_branches':[list(e) for e,v in closed.items() if not v],
            'sources':sorted(sources),'GFM':sorted(n for n,r in roles.items() if r=='GFM'),
            'GFL':sorted(n for n,r in roles.items() if r=='GFL'),'CB':cb_count,'SW':sw_count,
            'png_pixels':list(png.size),'dpi':list(png.info.get('dpi',[])),
            'workbook_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}


if __name__=='__main__':
    audit=[draw(10),draw(54)]
    (OUT/'topology_audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(audit,indent=2))
