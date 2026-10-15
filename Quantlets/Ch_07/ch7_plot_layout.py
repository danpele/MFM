"""Readable Chapter 7 charts at the size of their slide boxes."""
from pathlib import Path

def save_reviewed_figure(fig,name,folder):
    targets={'ch7_caviar','ch7_basel','ch7_precision','ch7_crk_table6','ch7_sem_b4_clusters'}
    if name not in targets:return False
    from slide_fit import _orig_savefig
    fig.set_size_inches(5.67,2.65)
    handles=[];labels=[]
    for ax in fig.axes:
        h,l=ax.get_legend_handles_labels()
        for hi,li in zip(h,l):
            if li not in labels:handles.append(hi);labels.append(li)
        ax.tick_params(labelsize=8)
        ax.xaxis.label.set_fontsize(9);ax.yaxis.label.set_fontsize(9)
        ax.title.set_fontsize(10)
        for t in ax.texts:t.set_fontsize(8)
        if ax.get_legend():ax.get_legend().remove()
    for leg in list(fig.legends):leg.remove()
    ax=fig.axes[0];ncol=2;legsize=8
    if name=='ch7_caviar':
        for line in ax.lines:
            if line.get_label().startswith('CAViaR'):line.set_zorder(5);line.set_linestyle('--');line.set_linewidth(1.2)
            elif line.get_label().startswith('FHS'):line.set_alpha(.65);line.set_linewidth(.8)
        ax.set_title('S&P 500: out-of-sample VaR 1%, 2016–2026',fontsize=10)
        labels=[('Daily loss (positive part)' if x.startswith('Daily loss') else 'CAViaR: fit 2000–2015' if x.startswith('CAViaR') else 'FHS: refit each January') for x in labels];ncol=3;legsize=7.5
        fig.subplots_adjust(left=.10,right=.99,top=.84,bottom=.25)
    elif name=='ch7_basel':
        ax.set_title('Historical simulation: ES/VaR ratios above bars',fontsize=10)
        ax.set_ylabel('Daily loss (%)');ax.margins(y=.22)
        fig.subplots_adjust(left=.10,right=.99,top=.84,bottom=.26)
    elif name=='ch7_precision':
        ax.set_title('S&P 500: 95% confidence intervals',fontsize=10)
        ax.set_xlabel('Daily loss (%); black tick = estimate',fontsize=9)
        ax.set_xlim(1.4,4.9)
        for t in ax.texts:t.set_visible(False)
        labels=['Asymptotic i.i.d.','Asymptotic HAC','i.i.d. bootstrap','Block bootstrap (20 days)']
        fig.subplots_adjust(left=.20,right=.99,top=.82,bottom=.31)
    elif name=='ch7_crk_table6':
        ax.set_title('S&P 500 VaR 1%: relative forecast errors',fontsize=10)
        ax.set_ylabel('Relative RMSFE (log scale)',fontsize=9)
        for t in ax.texts:
            if t.get_text()=='0.024':t.set_bbox(dict(facecolor='white',edgecolor='none',pad=.7))
            if 'Deep neural' in t.get_text():t.set_text('Deep neural networks')
            if 'Linear quantile' in t.get_text():t.set_text('Linear quantile regression = 1');t.set_fontsize(7.5)
        labels=[x.replace('Predictors: ','') for x in labels];ncol=4
        fig.subplots_adjust(left=.12,right=.99,top=.84,bottom=.32)
    elif name=='ch7_sem_b4_clusters':
        ax.set_position([.11,.66,.87,.19]);fig.axes[1].set_position([.11,.28,.36,.17]);fig.axes[2].set_position([.64,.28,.34,.17])
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
        ax.set_title(ax.get_title().replace('BET losses above','BET: above'),fontsize=9)
        fig.axes[2].set_title('VaR vs threshold',fontsize=9)
        fig.axes[2].set_xlabel('Exceedance share (%)',fontsize=8)
        labels=['Exceedances (alternating clusters)','Cluster maximum','Mean excess','GPD VaR 0.1%'];legsize=7.5
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.53,-.015),ncol=ncol,frameon=False,fontsize=legsize,handlelength=1.4,columnspacing=.9)
    for ext in ['pdf','png']:_orig_savefig(fig,Path(folder)/(name+'.'+ext),transparent=True,dpi=180)
    return True
