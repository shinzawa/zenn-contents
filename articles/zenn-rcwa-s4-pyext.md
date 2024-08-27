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
    #S.UseLessMemory();
    #S.UseLanczosSmoothing(False);
    # E polarized along the grating periodicity direction
    S.SetExcitationPlanewave(IncidenceAngles=(angle,0), sAmplitude=1, pAmplitude=0)

    S.SetFrequency(1/wave)

    incident,backward = S.GetPowerFlux(Layer='AirAbove')
    P = S.GetPowerFluxByOrder(Layer='Substrate')
    de_TE = P[2][0].real/incident.real

    # M polarized along the grating periodicity direction
    S.SetExcitationPlanewave(IncidenceAngles=(angle,0), sAmplitude=0, pAmplitude=1)
    S.SetFrequency(1.0/wave)

    incident,backward = S.GetPowerFlux(Layer='AirAbove')
    P = S.GetPowerFluxByOrder('Substrate', 0)
    de_TM = P[2][0].real/incident.real

    return de_TE, de_TM

print('depth', 'TE', 'TM')
for i in range(99):
    depth=0.0+i*0.05
    (de_TE, de_TM)=run_sim(depth)
    print(depth, de_TE, de_TM)

```rodis_01lambda_05depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_10lambda_05depth.png'
plot [0:5][0:1] "rodis_10lambda_05depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0

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

```
$ diff rodis_01lambda_05depth.py rodis_01lambda_50depth.py
47c47
<     depth=0.0+i*0.05
---
>     depth=45.0+i*0.05
```
```rodis_01lambda_50depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_01lambda_50depth.png'
plot [45:50][0:1] "rodis_01lambda_50depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0
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

```
$ diff rodis_01lambda_05depth.py rodis_10lambda_05depth.py 
6c6
<     multi = 1.0
---
>     multi = 10.0

```
```rodis_10lambda_05depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_10lambda_05depth.png'
plot [45:50][0:1] "rodis_01lambda_50depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0
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

```
$ diff rodis_01lambda_05depth.py rodis_10lambda_50depth.py 
6c6
<     multi = 1.0
---
>     multi = 10.0
47c47
<     depth=0.0+i*0.05
---
>     depth=45.0+i*0.05

```
```rodis_10lambda_50depth.gpl
set terminal png nocrop enhanced size 640,480 font "arial,12.0" 
set output 'rodis_10lambda_50depth.png'
plot [45:50][0:1] "rodis_01lambda_50depth.dat" u 1:2 ti "TE"  w linespoints lt 7 lc 'blue' lw 3.0, \
	 			"" u 1:3 ti "TM" w linespoints lt 7 lc 'red' lw 3.0
```
実行するには以下のようにします。
```
python3 rodis_10lambda_50depth.py
gnuplot rodis_10lambda_50depth.gpl
```
### rodis_10lambda_50depth.py の実行結果
rodis_10lambda_50depth.py の実行結果を以下に示します。
![](/images/Moharum_1995/rodis_10lambda_50depth.png)
