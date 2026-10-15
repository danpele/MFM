"""Chapter 13 figures: readable labels at their actual slide dimensions."""
from pathlib import Path

def save_course_figure(fig, name, folder):
    targets={
        'ch13_triple_barrier': ('Triple barriers: five S&P 500 events', (5.67,1.65)),
        'ch13_tree_complexity': ('Tree depth: training and validation accuracy', (5.67,2.23)),
        'ch13_expected_max_sharpe': ('Best Sharpe ratio among zero-skill strategies', (5.67,2.23)),
        'ch13_deflated_sharpe': ('DSR: 5 years; skew = −0.5; kurtosis = 6', (4.20,1.79)),
        'ch13_leakage_experiment': ('Random walk: no predictive signal', (3.29,1.78)),
        'ch13_model_comparison': ('', (5.67,1.65)),
    }
    if name not in targets:return False
    from slide_fit import _orig_savefig
    title,size=targets[name];fig.set_size_inches(*size)
    oldlegend=fig.axes[0].get_legend()
    barrier_handles=list(oldlegend.legend_handles) if name=='ch13_triple_barrier' and oldlegend else []
    for ax in fig.axes:
        ax.tick_params(labelsize=8)
        ax.xaxis.label.set_fontsize(8.5);ax.yaxis.label.set_fontsize(8.5)
        ax.title.set_fontsize(9)
        if len(fig.axes)==1:ax.set_title(title,loc='left',fontsize=9,pad=5)
        for text in ax.texts:text.set_fontsize(8)
        legend=ax.get_legend()
        if legend:legend.remove()
    if name=='ch13_triple_barrier':
        ax=fig.axes[0];ax.tick_params(labelsize=9);ax.set_ylabel('Index',fontsize=9)
        ax.set_title(title,loc='left',fontsize=10)
        fig.subplots_adjust(left=.11,right=.98,top=.78,bottom=.33)
        fig.legend(barrier_handles,['Upper barrier','Lower barrier','Horizon','Entry','First exit'],loc='lower center',bbox_to_anchor=(.53,-.025),ncol=5,frameon=False,fontsize=8.5,handlelength=1.1,columnspacing=.7)
    elif name=='ch13_model_comparison':
        fig.axes[0].set_title('S&P 500: purged 5-fold CV',loc='left',fontsize=9)
        fig.subplots_adjust(left=.095,right=.995,top=.82,bottom=.30,wspace=.38)
    elif name=='ch13_leakage_experiment':
        fig.subplots_adjust(left=.17,right=.98,top=.80,bottom=.27)
        fig.axes[0].yaxis.label.set_text('Accuracy')
        for text in fig.axes[0].texts:
            if 'Dashed line:' in text.get_text():text.set_position((.98,.88))
    else:
        ax=fig.axes[0];handles,labels=ax.get_legend_handles_labels()
        if name=='ch13_expected_max_sharpe':
            labels=['Expected maximum SR (theory)','Monte Carlo: mean ± 1 SD']
            ax.set_xlabel('Number of independent strategies tried, N',fontsize=8.5)
            ax.set_ylabel('Best annualised SR',fontsize=8.5)
        if name=='ch13_tree_complexity':
            for text in ax.texts:text.set_visible(False)
            ax.text(.02,.89,'Dashed: always up',transform=ax.transAxes,fontsize=8,bbox=dict(facecolor='white',edgecolor='none',pad=1))
            labels=['Tree: training','Tree: purged CV','Forest: purged CV']
        ncol=2 if name!='ch13_tree_complexity' else 3
        if name=='ch13_deflated_sharpe':
            labels=[x.replace('observed SR = ', 'SR = ') for x in labels];ncol=4
            ax.set_ylabel('DSR',fontsize=8.5)
        fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.52,-.015),ncol=ncol,frameon=False,fontsize=8,columnspacing=.8,handlelength=1.5)
        fig.subplots_adjust(left=.13,right=.99,top=.82,bottom=.36 if name=='ch13_deflated_sharpe' else .32)
    if name in {'ch13_tree_complexity','ch13_expected_max_sharpe'}:
        ax=fig.axes[0];ax.tick_params(labelsize=10)
        ax.xaxis.label.set_fontsize(10);ax.yaxis.label.set_fontsize(10)
        ax.set_title('Tree depth and accuracy' if 'tree_' in name else 'Best Sharpe among zero-skill strategies',loc='left',fontsize=11)
        for t in ax.texts:t.set_fontsize(9)
        for leg in list(fig.legends):leg.remove()
        labels=['Tree: train','Tree: CV','Forest: CV'] if 'tree_' in name else ['Expected maximum','Monte Carlo: mean ± SD']
        fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.53,-.02),ncol=len(labels),frameon=False,fontsize=10,columnspacing=.8,handlelength=1.4)
        ax.set_xlabel('Maximum depth' if 'tree_' in name else 'Independent strategies tried, N',fontsize=10)
        fig.subplots_adjust(left=.13,right=.98,top=.80,bottom=.35)
    for suffix in ['pdf','png']:
        _orig_savefig(fig,Path(folder)/(name+'.'+suffix),transparent=True,dpi=180)
    return True
