---
title: "rodisを用いたバイナリ格子のRCWA解析(2)"
emoji: "🌈"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["rodis","rcwa"]
published: true
---
# rodisでバイナリ格子のRCWA解析を試す。
## はじめに
前回rodisを用いた、RCWA解析の結果を紹介しましたが[Rodisを用いたバイナリ格子のRCWA解析](https://zenn.dev/tsuza/articles/zenn-rcwa-examples)、そのなかのある条件では、計算が収束せず、グラフに表示されませんでした。
この記事では、rodisの改修を行い、Moharamの論文の条件での、収束した解析結果を紹介します。
## rodisのインストール
rodisのインストールは、前回の記事で紹介しましたのでそちらをご覧ください。

## rodis ソースコードの改修
前回は、ソースコードの改変なしで、環境設定のみubuntu-22.04に合わせて、RCWA解析を実行しました。ただ、4つある条件のうち、3番目と4番目のConicalでの結果が、収束せず、グラフにはTEとTMしか表示されない状態になりました。解析の結果2次の偏微分方程式（参考文献の例えば式（15））に対応する右辺の行列の固有値を求めた後、その固有値の正の平方根を用いてそのあとの解を表現しているので、ubuntu-22.04の環境で、そうなるように調整します。具体的には、固有値、固有ベクトルを求める関数、CompleEigenの直後で、以下のように、元のコードをコメントアウトして、
```cpp:Grating1DC.cxx
              W1=ComplEigen(W1,L1);
              W2=ComplEigen(W2,L2);
  for(i=0;i<n;i++) 
  {
//     L1(i,0)=sqrt(L1(i,0));
//    if(real(L1(i,0))<-1e-8) L1(i,0)=-L1(i,0);

//     L2(i,0)=sqrt(L2(i,0));
//    if(real(L2(i,0))<-1e-8) L2(i,0)=-L2(i,0);
    if (sqrt(L1(i,0)).imag() < 0.0)
        L1(i,0)=conj(sqrt(L1(i,0)));
    else
        L1(i,0)=sqrt(L1(i,0));

    if (sqrt(L2(i,0)).imag() < 0.0)
        L2(i,0)=conj(sqrt(L2(i,0)));
    else
        L2(i,0)=sqrt(L2(i,0));
```
のように、変更しています。
TE,TMも同様に変更して、変化しないことを確認します。
```cpp:GratingTE1DM.cxx
  W=ComplEigen(W,L);
  for(i=0;i<n;i++)
  {
    //  L(i,0)=sqrt(L(i,0));
    // if(real(L(i,0))<0) L(i,0)=-L(i,0);
    if (sqrt(L(i,0)).imag() < 0.0)
        L(i,0)=conj(sqrt(L(i,0)));
    else
        L(i,0)=sqrt(L(i,0));
  }
```
```cpp:GratingTM1DM.cxx
    W=ComplEigen(W,L);
    for(i=0;i<n;i++)
    {
    // L(i,0)=sqrt(L(i,0));
    // if(real(L(i,0))<0) L(i,0)=-L(i,0);
    if (sqrt(L(i,0)).imag() < 0.0)
        L(i,0)=conj(sqrt(L(i,0)));
    else
        L(i,0)=sqrt(L(i,0));
    }
```
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
![](/images/Moharam_1995-2/moharam1995_lambda_5lambda.png)

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
![](/images/Moharam_1995-2/moharam1995_lambda_50lambda.png)

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
![](/images/Moharam_1995-2/moharam1995_10lambda_5lambda.png)

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
![](/images/Moharam_1995-2/moharam1995_10lambda_50lambda.png)

## まとめ
- Rodisのソースコードの改修方法を紹介しました。
- 改修したRodisを用いてMoharamの論文の例題を実行し、解析結果を示しました。
- 解析結果は 1次元の格子に対して、TE,TMおよびConicalのそれぞれの光入射条件でMoharamの論文の特性をほぼ再現しました。

## 参考文献
- M. G. Moharam, E. B. Grann, D. A. Pommet, and T. K. Gaylord, “Formulation for stable and eﬃcient implementation of the rigorous coupled-wave analysis of binary gratings,” J. Opt. Soc. Am. A 12(5), pp. 1068–1076, 1995