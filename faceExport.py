# FACE EXPORTER 2021.0223
#
#  概要
#       - DFLで顔検出する際に、同時に元画像の顔周辺を劣化なしで静止画に保存。
#           - 顔検出エリアを上下左右に広げてそのまま保存。
#           - 顔セット画像のように拡大縮小や回転は行わないため劣化なし。
#           - そのため、保存した画像の解像度はバラバラになる。
#
#  目的
#       - 顔セット再構築の手間を大幅に省くこと。
#           - 何らかの理由で顔セットを作り直さなければならないことがある。
#           - 例えば、DFアプリを乗り換える、DFアプリの仕様が変わった、違うサイズの顔セットを作りたいなど。
#           - その時、動画→静止画→不要フレーム削除→顔検出→不要顔削除をもう一度やることになる。
#       - 本ツールで保存した顔周辺の画像を蓄積しておけば、顔検出を再度実行するだけで済む(ほぼ)。
#
#   構成
#       - faceExport.py : 保存処理を行う。
#       - Extractor.py  : DFLに存在する顔検出モジュール。faceExport.pyを呼び出す改造を行ったもの。
#
#   対応バージョン
#       - DFL 2020.08.02
#       - DFL 2021.01.04
#
#  インストール
#       - \_internal\DeepFaceLab\mainscripts\Extractor.py を上書きするため、念のためオリジナルの
#           Extractpr.py を Extractor_org.py のように名前を変えて残しておく。
#       - Extractor_XXXX.XXXX.py を上記フォルダにコピーして、Extractor.py にリネームする。
#       - faceExport.py を上記フォルダにコピーする。
#
#   カスタマイズ
#       - 下の方にある、カスタマイズ用変数を必要に応じて変更する。
#       - 保存先フォルダパス : 保存先のフォルダの古パス。フォルダは作っておく。
#       - 小さい画像保存先フォルダ名 : 小さい顔はこのフォルダに保存する。フォルダは作っておく。
#       - ファイル名プリフィックス : 画像ファイル名の先頭に付ける文字列。
#       - 拡張子 : 保存形式の指定。無劣化保存(推奨)なら .png を指定。.jpg も指定可能。
#       - マージン : 顔検出した矩形を上下左右にどれだけ広げるかの比率。
#           - 0.0 だと元の矩形のまま出力。
#           - 1.0 にすると、元の矩形の9倍の面積になる。
#       - サイズ境界 : 顔検出矩形の両辺がこの値未満の場合、小さい画像保存先フォルダへ保存する。
#       - 実行フラグ : FaceExportを実行したくない場合、Falseにする。
# 
#  実行方法
#       - 顔検出を行うバッチ 4) data_src faceset extract.bat などを実行する。
#       - 顔検出を行うたびに、画像が出力される。
#
#   注意事項
#       - 顔の周辺を広めに切り取るため、近くにいる別の人の顔を含むことがある。
#       - 別の人が写りこんでいる場合、トリミングしたり黒塗りにするなどして再保存する。このためにもPNG保存推奨。
#
#   Extractor.py の変更箇所
#       rects_stage メソッドの return の直前に以下の2行を追加しているだけ。
#       新しいDFLがリリースされても、大幅な変更がなければ recs_stage の最後に埋めれば動作するはず。
#
#       159    from . import faceExport
#       160    faceExport.run( data.rects, rotated_image )
#

import cv2
import time
import math

# カスタマイズ用変数

# gExportDirPath  = 'k:\\faceExp\\'           # 保存先フォルダパス (Windows)
gExportDirPath  = '/content/drive/MyDrive/faceExporter/face_out/'           # 保存先フォルダパス (GoogleColab)
gExportSmall    = '_small'                  # 小さい画像保存先フォルダ名
gFilePrefix     = 'f_'                      # ファイル名プリフィックス (ファイル名の先頭につける文字列)
gFileSuffix     = '.png'                    # ファイルの拡張子 '.png' or '.jpg'
gMarginRate     = 0.7                       # マージン ( 1.0 だと、顔9個分の面積になる )
gMinSize        = 200                       # サイズ境界 顔の両方の辺がこれ未満の場合は gExportSmall へ出力する

gRun            = True                      # 実行したくないときは False

def run( rects, srcImage ):

    if ( gRun == False ):
        return

    hImg, wImg, chImg = srcImage.shape

    rects = sorted( rects, key = lambda x : x[0] )

    for rect1 in rects:

        (l,t,r,b)   = rect1

        wFace       = r - l
        hFace       = b - t

        isSmall = True if ( wFace < gMinSize ) and ( hFace < gMinSize ) else False

        wFace = math.floor( wFace * gMarginRate )
        hFace = math.floor( hFace * gMarginRate )

        lHead = l - wFace
        rHead = r + wFace
        tHead = t - hFace
        bHead = b + hFace

        # 画像の外にはみ出さないように補正

        if ( lHead < 0 ) :
            lHead = 0
        
        if ( wImg < rHead ) :
            rHead = wImg

        if ( tHead < 0 ) :
            tHead = 0

        if ( hImg < bHead ) :
            bHead = hImg

        faceImage = srcImage[tHead:bHead,lHead:rHead]       # トリミング

        fileName = gFilePrefix + ( str( math.floor( time.time() * 10000 ) - 15900000000000 ) + '_[' + str( ｒHead - lHead ) + 'x' + str( bHead - tHead ) + ']' + gFileSuffix )
        if isSmall == False :
            filePath = gExportDirPath + fileName
        else :
            filePath = gExportDirPath + gExportSmall + '/' + fileName

        cv2.imwrite( filePath, faceImage, [ cv2.IMWRITE_JPEG_QUALITY, 100 ] )
