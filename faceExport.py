# FACE EXPORTER 2020.0906
#
#  目的
#    - 顔抽出時に、data_src 直下の画像の画像の顔周辺を切り出した画像を出力する。
#    - 切り出すときに、拡大縮小も回転も行わない。
#    - 顔セットの仕様が変わったときなど、顔セットの作り直しの時のために素材を高画質で残す目的。
#    - 画像全体を残すのに比べると、必要な人の顔周辺だけにできるため、おっさん除去などを済ませた画像になる。
#
#  インストール
#    - DFL 2020.08.02 版に適用可能。
#    - \_internal\DeepFaceLab\mainscripts\Extractor.py を書き換えるため、念のため Extractpr_org.py
#      のように名前を変えて残しておく。
#    - Extractor.py と faceExport.py を上記フォルダにコピーする。
#
#   カスタマイズ
#   - 出力先は、gExportDirPath に記載しておき、フォルダも事前に作成しておく。
#
#   注意事項
#   - 顔の周辺を広めに切り取るため、近くにいる別の人の顔を含むことがあります。
#   - PNGで出力しておけば、黒塗りにするなどして再保存しても劣化がないのでおすすめです。
#
#   Extractor.py の変更箇所
#       rects_stage メソッドの return の直前に以下の2行を追加。
#
#       159    from . import faceExport
#       160    faceExport.run( data.rects, rotated_image )
#

import cv2
import time
import math

gExportDirPath  = 'k:\\faceExp\\'           # 保存先フォルダパス
gExportSmall    = '_small'                  # 小さい画像保存先フォルダ名
gFilePrefix     = 'f_'                      # ファイル名の前につける文字列
gFileSuffix     = '.png'                    # ファイルの拡張子 '.png' or '.jpg'
gMarginRate     = 0.7                       # 顔の外側のマージン比率 ( 1.0 だと、顔9個分の面積になる )
gMinSize        = 80                        # 顔の両方の辺がこれ未満の場合は出力しない

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

        if ( lHead < 0 ) :
            lHead = 0
        
        if ( wImg < rHead ) :
            rHead = wImg

        if ( tHead < 0 ) :
            tHead = 0

        if ( hImg < bHead ) :
            bHead = hImg

        faceImage = srcImage[tHead:bHead,lHead:rHead]       # トリミング

        fileName = gFilePrefix + ( str( math.floor( time.time() * 10000 ) - 15900000000000 ) + gFileSuffix )
        if isSmall == False :
            filePath = gExportDirPath + fileName
        else :
            filePath = gExportDirPath + gExportSmall + '\\' + fileName

        cv2.imwrite( filePath, faceImage, [ cv2.IMWRITE_JPEG_QUALITY, 100 ] )
