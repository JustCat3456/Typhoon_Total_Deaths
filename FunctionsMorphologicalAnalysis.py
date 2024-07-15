#################################################
# 20200721
# 文章を形態素解析する関数群
# cf:https://qiita.com/segavvy/items/e0a7994cc63c8be7380b
#################################################

# coding: utf-8
import pandas as pd
import MeCab
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

##########################################
# 形態素解析結果を順次読み込んで、各形態素を
# ・表層形（surface）
# ・基本形（base）
# ・品詞（pos）
# ・品詞細分類1（pos1）
# の4つをキーとする辞書に格納し、1文ずつ、この辞書のリストとして返す
# 
# 戻り値：
# 1文の各形態素を辞書化したリスト
##########################################
def docu_lines(fname_parsed, pos = ["名詞", "形容詞", "動詞","副詞", "助詞", "助動詞", "連体詞"]):
    with open(fname_parsed) as file_parsed:
        morphemes = []
        for line in file_parsed:
            #example of line : メロス	名詞,一般,*,*,*,*,*
            #print(line)
            
            #改行コード,スペースの削除
            line = line.replace('\r','')
            line = line.replace('\n','')


            # 表層形はtab区切り、それ以外は','区切りでバラす
            cols = line.split('\t')
            if(len(cols) < 2):
                return     # 区切りがなければ終了
            res_cols = cols[4].split('-')
            
            #print(cols)
            #print(res_cols)
            
            if cols[0] == '*':
                print(cols[0])
            
            # 辞書作成、リストに追加
            morpheme = {
                'surface': cols[0],     #表層形
                #'base': res_cols[6],  #基本形
                'pos': res_cols[0],    #品詞
                'pos1': res_cols[-1]   #品詞細分類1
            }
            if res_cols[0] in pos and (cols[0] != '*'):
                morphemes.append(morpheme)

            # 品詞細分類1が'句点'なら文の終わりと判定
            if res_cols[-1] == '句点':
                #print(line)
                yield morphemes
                morphemes = []

                

##########################################
# 文章を形態素解析
# ファイル（fname）を形態素解析して保存する(fname_parsed)
##########################################
def get_word_freq_from_document(file_doc, pos):
    file_part1,file_part2 = file_doc.split('.')
    #print(file_part1,file_part2)
    file_parsed = file_part1 + '_mecab.' +file_part2
    #print(file_parsed)
    
    
    with open(file_doc, encoding='utf-8') as data_file,  open(file_parsed, mode='w') as out_file:
        mecab = MeCab.Tagger("mecabrc")###2022.01.24 引数に"mecabrc"を追加．M1 macではデフォルトが"mecabrc"でないため
        out_file.write(mecab.parse(data_file.read()))
    
    # Counterオブジェクトに単語をセット
    word_counter = Counter()
    for line in docu_lines(file_parsed, pos=pos):
        #print(line)
        word_counter.update([morpheme['surface'] for morpheme in line])

    # 全件取得
    list_word_freq = word_counter.most_common()

    #print(list_word)

    # 出現数のリスト取得
    list_word, list_freq = list(zip(*list_word_freq))
    #print(*list_word)
    
    #データフレームに変換
    df_word_freq = pd.DataFrame({'word':list_word, 'frequency':list_freq})
    #print(df_word)
    
    #Probの列を追加
    df_word_freq['Prob'] = df_word_freq['frequency']/df_word_freq['frequency'].sum()
    
    #総単語数，異なり単語数を表示
    n_word_total = df_word_freq['frequency'].sum()
    n_word_different = len(df_word_freq.index)
    print('総単語数={}，異なり単語数={}'.format(n_word_total, n_word_different))
    
    return(df_word_freq)
    

        