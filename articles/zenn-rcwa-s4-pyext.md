---
title: "S4_pyextを用いたバイナリ格子のRCWA解析"
emoji: "🌈"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["S4", "pyext","rcwa"]
published: false
---
# S4_pyextでバイナリ格子のRCWA解析を試す。
## はじめに
この記事では、RCWA解析光学シミュレータとして公開されているS4の新しいバージョンのインストールを行い、RCWA解析の例として、1次元バイナリ格子の解析結果を紹介します。
## S4_pyextのインストール
S4_pyextのインストールは、基本的に

https://github.com/phoebe-p/S4

のREADMEを参照すればよいと思います。

https://hakasekatei.com/rcwaprg-1/

に実際に、インストールした例があります。Windowsへのとありますが、WSL上のubuntuへのインストールと思われます。私は、ubuntu22.04で行いました。

## バイナリ格子のRCWA解析

実行するためのpython入力ファイルrodis_01lambda_05depth.pyは以下の通りです。
### 実行スクリプト（rodis_01lambda_05depth.py）
```py:rodis_01lambda_05depth.py
import S4

def run_sim(depth):
    n2 = 2.04
    wave = 1.55
    multi = 1.0
    Lambda = wave*multi
    angle = 10.0
    lpsi = 0.7071067811140325
	
    S = S4.New( Lattice = Lambda, NumBasis = 99 )

    # Material definition
    S.AddMaterial(Name="FusedSilica", Epsilon=n2**2)
    S.AddMaterial(Name="Vacuum", Epsilon=1)

    S.AddLayer(Name='AirAbove', Thickness=0, Material='Vacuum')
    S.AddLayer(Name='Grating', Thickness=depth*wave, Material='Vacuum')
    S.SetRegionRectangle(Layer='Grating',
                         Material='FusedSilica',
                         Center=(0.5*Lambda,0),
                         Angle=0,
                         Halfwidths=(0.25*Lambda, 0))
    S.AddLayer(Name='Substrate', Thickness=0, Material='FusedSilica')
    # E polarized along the grating periodicity direction
    S.SetExcitationPlanewave(IncidenceAngles=(angle,0), sAmplitude=1, pAmplitude=0)

    S.SetFrequency(1.0/wave)

    incident,backward = S.GetPowerFlux(Layer='AirAbove')
    P = S.GetPowerFluxByOrder(Layer='Substrate')
    de_TE = P[2][0].real/incident.real

    # M polarized along the grating periodicity direction
    S.SetExcitationPlanewave(IncidenceAngles=(angle,0), sAmplitude=0, pAmplitude=1)
    S.SetFrequency(1.0/wave)

    incident,backward = S.GetPowerFlux(Layer='AirAbove')
    P = S.GetPowerFluxByOrder('Substrate', 0)
    de_TM = P[2][0].real/incident.real

    # Conical polarized along the grating periodicity direction
    S.SetExcitationPlanewave(IncidenceAngles=(angle,30), sAmplitude=lpsi, pAmplitude=lpsi)

    S.SetFrequency(1/wave)
    incident,backward = S.GetPowerFlux(Layer='AirAbove')
    P = S.GetPowerFluxByOrder(Layer='Substrate')
    de_Conical = P[2][0].real/incident.real
    
    return de_TE, de_TM, de_Conical

print('depth', 'TE', 'TM', 'Conical')
for i in range(99):
    depth=0.0+i*0.05
    (de_TE, de_TM, de_Conical)=run_sim(depth)
    print(depth, de_TE, de_TM, de_Conical)

```

```gpl:rodis_01lambda_05depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_01lambda_05depth.png'
plot [0:5][0:1] "rodis_01lambda_05depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0,\
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0,\
				"" u 1:4 ti "Conical"  w linespoints lt 7 lc 'black' lw 3.0

```

実行するには以下のようにします。
```
python3 rodis_01lambda_05depth.py
gnuplot rodis_01lambda_05depth.gpl
```
### rodis_01lambda_05depth.py の実行結果
rodis_01lambda_05depth.py の実行結果を以下に示します。
![](/images/Moharum_1995/rodis_01lambda_05depth.png)

つぎに条件を変更したrodis_01lambda_50depth.pyとの差分を示します。

```diff py:rodis_01lambda_05depth.py, rodis_01lambda_50depth.py
47c47
<     depth=0.0+i*0.05
---
>     depth=45.0+i*0.05
```
```txt: rodis_01lambda_50depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_01lambda_50depth.png'
plot [45:50][0:1] "rodis_01lambda_50depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0,\
				"" u 1:4 ti "Conical"  w linespoints lt 7 lc 'black' lw 3.0
```
実行するには以下のようにします。
```
python3 rodis_01lambda_50depth.py
gnuplot rodis_01lambda_50depth.gpl
```
### rodis_01lambda_50depth.py の実行結果
rodis_01lambda_50depth.py の実行結果を以下に示します。
![](/images/Moharum_1995/rodis_01lambda_50depth.png)

つぎに条件を変更したrodis_10lambda_05depth.pyとの差分を示します。

```diff py:rodis_01lambda_05depth.py rodis_10lambda_05depth.py 
6c6
<     multi = 1.0
---
>     multi = 10.0

```
```txt: rodis_10lambda_05depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_10lambda_05depth.png'
plot [45:50][0:1] "rodis_01lambda_50depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0,\
				"" u 1:4 ti "Conical"  w linespoints lt 7 lc 'black' lw 3.0
```
実行するには以下のようにします。
```
python3 rodis_10lambda_05depth.py
gnuplot rodis_10lambda_05depth.gpl
```
### rodis_10lambda_05depth.py の実行結果
rodis_10lambda_05depth.py の実行結果を以下に示します。
![](/images/Moharum_1995/rodis_10lambda_05depth.png)

つぎに条件を変更したrodis_10lambda_50depth.pyとの差分を示します。

```diff py:rodis_01lambda_05depth.py rodis_10lambda_50depth.py 
6c6
<     multi = 1.0
---
>     multi = 10.0
47c47
<     depth=0.0+i*0.05
---
>     depth=45.0+i*0.05

```
```txt: rodis_10lambda_50depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_10lambda_50depth.png'
plot [45:50][0:1] "rodis_01lambda_50depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0,\
				"" u 1:4 ti "Conical"  w linespoints lt 7 lc 'black' lw 3.0
```
実行するには以下のようにします。
```
python3 rodis_10lambda_50depth.py
gnuplot rodis_10lambda_50depth.gpl
```
### rodis_10lambda_50depth.py の実行結果
rodis_10lambda_50depth.py の実行結果を以下に示します。
![](/images/Moharum_1995/rodis_10lambda_50depth.png)

## まとめ
- RCWA解析を可能とする光シミュレータのひとつであるS4_pyextのインストール手順を示しました。
- S4_pyextを用いてMoharamの論文の例題を実行し、解析結果を示しました。
- 解析結果は 1次元の格子に対して、TE,TMのそれぞれの光入射条件でMoharamの論文の特性をほぼ、再現しました。TMでは若干ずれが生じました。
- Conicalでは結果が得られませんでした。
  
## 参考文献
- M. G. Moharam, E. B. Grann, D. A. Pommet, and T. K. Gaylord, “Formulation for stable and eﬃcient implementation of the rigorous coupled-wave analysis of binary gratings,” J. Opt. Soc. Am. A 12(5), pp. 1068–1076, 1995