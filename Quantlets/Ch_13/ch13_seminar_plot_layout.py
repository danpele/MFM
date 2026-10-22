"""Final-size layout for the seminar's multi-panel figures; data are unchanged."""
from pathlib import Path

def save_seminar_figure(fig,name,folder):
    names={'a1_weights','a2_task','a2_paths','a3_task','a3_purge','a8_auc','b3_auc','b3_models','b3_importance','b10_pt','b6_grid','b5_memory','b11_meta'}
    key=name.removeprefix('ch13_sem_')
    if not name.startswith('ch13_sem_') or key not in names:return False
    from slide_fit import _orig_savefig
    small=key in {'a2_task','a2_paths','a3_task','a3_purge'}
    fig.set_size_inches(*( (2.90,2.02) if small else (5.67,2.23)))
    legends=[]
    for leg in fig.legends:
        legends.append((leg.legend_handles,[t.get_text() for t in leg.get_texts()]))
        leg.remove()
    for ax in fig.axes:
        ax.tick_params(labelsize=7.5)
        ax.xaxis.label.set_fontsize(8);ax.yaxis.label.set_fontsize(8)
        for t in ax.texts:t.set_fontsize(7.5)
        ax.title.set_fontsize(8)
    if key.startswith('a2_'):
        for j,ax in enumerate(fig.axes):
            ax.set_position([.15,.67-j*.35,.80,.20]);ax.set_title('Path '+str(j+1)+' (days)',loc='left',fontsize=8,pad=3)
            ax.set_xlabel('',fontsize=8)
            if j==0:ax.tick_params(labelbottom=False)
            ax.margins(y=.3)
            if key=='a2_paths':ax.set_ylim(97.2,103.5)
            for text in ax.texts:
                x,y=text.get_position()
                if key=='a2_task' and x>=5:
                    text.set_ha('right')
                    if j==1:text.set_position((x,y+.5))
                if key=='a2_paths':
                    text.set_position((.25,y+(.3 if y<100 else -.3)));text.set_va('center')
            ax.set_xticks(range(6));ax.tick_params(pad=1)
        if legends:
            h,l=legends[0];l=[x.replace('first touch / exit','exit').replace('vertical barrier','horizon').replace(' barrier','') for x in l]
            fig.legend(h,l,loc='lower center',bbox_to_anchor=(.55,-.025),ncol=3,frameon=False,fontsize=7,handlelength=1,columnspacing=.6)
    elif key.startswith('a3_'):
        ax=fig.axes[0];ax.set_title('Label spans: test observations 8–11',loc='left',fontsize=8)
        ax.set_xlabel('day',fontsize=8);ax.set_ylabel('observation',fontsize=8)
        ax.set_xticks(range(0,20,4));ax.set_yticks(range(0,20,4))
        fig.subplots_adjust(left=.18,right=.98,top=.83,bottom=.40)
        if legends:
            h,l=legends[0];l=[x.replace('embargo (its label also overlaps)','embargo').replace('purged: span overlaps the test labels','purged').replace('not yet classified','classify') for x in l]
            fig.legend(h,l,loc='lower center',bbox_to_anchor=(.55,-.02),ncol=2,frameon=False,fontsize=7.5,handlelength=1.3)
    else:
        fig.subplots_adjust(left=.09,right=.99,top=.83,bottom=.38,wspace=.62)
        if key=='b3_auc':
            ax=fig.axes[0];ax.set_yticklabels(['DeLong','L = 1','L = 20','L = 60']);ax.set_title('RF AUC: 95% intervals',loc='left',fontsize=8)
            for t in ax.texts:t.set_visible(False) # intervals are printed numerically beneath the chart
            fig.axes[1].set_title('Bootstrap estimates',loc='left',fontsize=8)
            fig.axes[1].set_xlabel('AUC (not a null distribution)',fontsize=8)
        if key=='a8_auc':
            ax=fig.axes[0];ax.set_xticklabels([t.get_text().removeprefix('neg ') for t in ax.get_xticklabels()]);ax.set_yticklabels([t.get_text().removeprefix('pos ') for t in ax.get_yticklabels()]);ax.set_xlabel('negative score',fontsize=8);ax.set_ylabel('positive score',fontsize=8)
            ax.set_title('Pair comparisons: U = 7',loc='left',fontsize=8)
            fig.axes[1].set_xlabel('False positive rate',fontsize=7.5);fig.axes[1].set_ylabel('True positive rate',fontsize=7.5)
            fig.axes[2].set_xlabel('U: 20 label allocations',fontsize=8)
            fig.axes[2].set_title('Exact null distribution',loc='left',fontsize=8)
        if key=='b11_meta':
            fig.axes[0].set_ylim(0,1.48)
            for i,t in enumerate(fig.axes[0].texts):
                x,y=t.get_position();t.set_position((x,y+(.28 if i%2==0 else .01)));t.set_color('black');t.set_ha('center');t.set_va('bottom')
            fig.axes[1].set_xlabel('Gross log return / trade',fontsize=8)
            fig.axes[1].set_title('Kept and skipped trades',loc='left',fontsize=8)
        if key=='b3_models':
            fig.axes[0].set_title('Accuracy: five purged folds',loc='left',fontsize=8)
            fig.axes[1].set_title('AUC: five purged folds',loc='left',fontsize=8)
            for ax in fig.axes:ax.set_ylim(.40,.71);ax.set_xticklabels(['Logit-L1','Random\nForest','Boosting'])
        if key=='b3_importance':
            titles=['MDI: in sample','MDA: AUC drop','Mean absolute SHAP']
            for ax,title in zip(fig.axes,titles):ax.set_title(title,loc='left',fontsize=8)
            fig.subplots_adjust(left=.14,wspace=.4,top=.90,bottom=.30)
        if key=='b5_memory':
            for ax,title in zip(fig.axes,['ADF statistic','Correlation with log price','Memory estimates']):ax.set_title(title,loc='left',fontsize=8)
            fig.axes[2].set_xlabel('Memory; 95% CI',fontsize=8)
            for ax,pos in zip(fig.axes[:3],[[.08,.40,.20,.43],[.40,.40,.17,.43],[.79,.40,.19,.43]]):ax.set_position(pos)
            fig.axes[2].set_yticklabels(['log price (ELW)','FFD (ELW)','returns (LW)','|returns| (LW)'])
            fig.axes[2].set_ylim(3.6,-.95)
            fig.axes[2].set_xlim(-.25,1.3)
            for text in fig.axes[2].texts:
                if hasattr(text,'xyann'):
                    # value above its own marker, clear of the interval and of the neighbouring rows
                    text.xy=(float(text.get_text()),text.xy[1]);text.xyann=(0,4);text.set_ha('center');text.set_va('bottom')
                    text.set_bbox(dict(facecolor='white',edgecolor='none',alpha=.9,pad=.3))
            fig.axes[0].set_ylabel('')
        if key=='a1_weights':
            for ax,title in zip(fig.axes,['Absolute weights','Partial sums','Decomposition']):ax.set_title(title,loc='left',fontsize=8)
        if key=='b6_grid':
            for ax,title in zip(fig.axes[:3],['120 trading rules','Trial correlations','Selected-rule DSR']):ax.set_title(title,loc='left',fontsize=8)
            ax=fig.axes[0];ticks=ax.get_xticks();labels=[t.get_text() for t in ax.get_xticklabels()];ax.set_xticks(ticks[::3],labels[::3])
            fig.subplots_adjust(bottom=.43,wspace=.58)
        if key=='a1_weights':fig.subplots_adjust(bottom=.43)
        if legends:
            h,l=legends[0]
            l=[x.replace('always up:','always up:').replace(' (share of up labels)','').replace('bootstrap AUC, ','bootstrap ').replace('observed pooled AUC','observed AUC') for x in l]
            if key=='b6_grid':
                l=[x.replace('selected rule (5, 40): SR 1.19','Selected rule').replace('V = dispersion of the 120 SRs','V: empirical SR dispersion').replace('V = 1/T (independent trials)','V = 1/T').replace('share of variance','variance share').replace('0.95 threshold','DSR = 0.95') for x in l]
            cols=2 if key in {'b3_auc','b11_meta','b3_importance','b3_models'} else 3
            fig.legend(h,l,loc='lower center',bbox_to_anchor=(.52,-.025),ncol=cols,frameon=False,fontsize=7.2,handlelength=1.3,columnspacing=.8)
    if key in {'b3_auc','b11_meta'}:
        for ax in fig.axes:
            ax.tick_params(labelsize=9)
            ax.xaxis.label.set_fontsize(9);ax.yaxis.label.set_fontsize(9)
            ax.title.set_fontsize(9)
            for t in ax.texts:t.set_fontsize(9)
        for legend in fig.legends:
            for t in legend.get_texts():t.set_fontsize(8.5)
    if key=='b3_auc':fig.subplots_adjust(left=.14)
    if key in {'b11_meta','a1_weights','a2_paths','a2_task'}:
        for ax in fig.axes:
            for t in ax.texts:
                t.set_bbox(dict(facecolor='white',edgecolor='none',alpha=.92,pad=.5))
    if key=='a1_weights':
        for t in fig.axes[1].texts:
            x,y=t.get_position();t.set_position((x,y+.02))
    for suffix in ['pdf','png']:_orig_savefig(fig,Path(folder)/(name+'.'+suffix),transparent=True,dpi=180)
    return True
