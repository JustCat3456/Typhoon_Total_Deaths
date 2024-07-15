# coding: utf-8

###################################################
# 20200727
# 散布図，ヒストグラム，相関係数行列を描画する
# cf: https://qiita.com/Gomesu39/items/d52a8110a733460cd072
###################################################

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
#from pandas.plotting._matplotlib.tools import _set_ticks_props, _subplots 
from pandas.plotting._matplotlib.tools import create_subplots ### 2021.07.06 新たなモジュールでは_subplots→create_subplotsに変更されたため．_set_ticks_propsは使っていなかったので削除

from pandas.core.dtypes.missing import notna

def  matrix_histogram_scatter_correlation(
    df,
    alpha=0.5,
    figsize=None,
    ax=None,
    grid=False,
    diagonal="hist",
    marker=".",
    density_kwds=None,
    hist_kwds=None,
    range_padding=0.05,
    method = "pearson",
    **kwds
):


    def _get_marker_compat(marker):

        if marker not in mlines.lineMarkers:
            return "o"
        return marker

    #print(df)
    n = df.columns.size
    naxes = n * n
    fig, axes = create_subplots(naxes=naxes, figsize=figsize, ax=ax, squeeze=False)

    # no gaps between subplots
    fig.subplots_adjust(wspace=0, hspace=0)

    mask = notna(df)

    marker = _get_marker_compat(marker)

    hist_kwds = hist_kwds or {}
    density_kwds = density_kwds or {}

    # GH 14855
    kwds.setdefault("edgecolors", "none")

    boundaries_list = []
    
    # calc correlation
    df_corr = df.corr(method = method) 
    #print(df_corr)
    
    for a in df.columns:
        values = df[a].values[mask[a].values]
        rmin_, rmax_ = np.min(values), np.max(values)
        rdelta_ext = (rmax_ - rmin_) * range_padding / 2.0
        boundaries_list.append((rmin_ - rdelta_ext, rmax_ + rdelta_ext))

    for i, a in enumerate(df.columns):
        for j, b in enumerate(df.columns):
            ax = axes[i, j]
            ax.set_visible(False)  # 一旦非表示にしておき、あとで必要なものだけ表示する

            if i == j:
                values = df[a].values[mask[a].values]

                # Deal with the diagonal by drawing a histogram there.
                if diagonal == "hist":
                    n_hist, bins, pathces =  ax.hist(values, **hist_kwds)
                    #print(n_hist)
                    ax.set_ylim(0, max(n_hist)*1.2)

                elif diagonal in ("kde", "density"):
                    from scipy.stats import gaussian_kde

                    y = values
                    gkde = gaussian_kde(y)
                    ind = np.linspace(y.min(), y.max(), 1000)
                    ax.plot(ind, gkde.evaluate(ind), **density_kwds)

                #データのラベル
                ax.annotate(a, xy=(0.5, 0.85), xycoords='axes fraction', fontsize=14,
                horizontalalignment='right', verticalalignment='bottom', ha = 'center')
                
                #ax.set_xlim(boundaries_list[i])
                ax.set_visible(True)

            elif i > j:
                common = (mask[a] & mask[b]).values

                ax.scatter(
                    df[b][common], df[a][common], marker=marker, alpha=alpha, **kwds
                )
                
                #print(b,a)
                #print(df[b][common], df[a][common])

                ax.set_xlim(boundaries_list[j])
                ax.set_ylim(boundaries_list[i])
                ax.set_visible(True)

            ax.set_xlabel(b)
            ax.set_ylabel(a)

            
            if j != 0:
                ax.yaxis.set_visible(False)
            if i != n - 1:
                ax.xaxis.set_visible(False)

            
            
            #相関係数のプロット
            if i < j:
                #print(i,j)
                ax.scatter(
                    [0], [0], marker=marker, alpha=alpha,color='white', **kwds
                )
                
                ax.annotate('{:.2f}'.format(df_corr[a][b]), xy=(0.7, 0.4), xycoords='axes fraction', fontsize=20,
                horizontalalignment='right', verticalalignment='bottom')
                
                ax.set_visible(True)
            
            
    plt.show()

    return