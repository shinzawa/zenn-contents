---
title: "Rodisを用いたバイナリ格子のRCWA解析"
emoji: "🌈"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["rodis","rcwa"]
published: false
---
## Rodisでバイナリ格子のRCWA解析を行う
参考：["Rigorous coupled-wave analysis (RCWA) of binary gratings using RODIS"](https://elsonliu.wordpress.com/2011/08/28/rigorous-coupled-wave-analysis-rcwa-of-binary-gratings-using-rodis/)
### Rodisのインストール
[rodis のソース](http://photonics.intec.ugent.be/research/facilities/design/rodis/)
ここにwindows と unix の source code が別々に置いてある。
今回は unix の方(rodis.tar.gz)をdown load する。

- OS: ubuntu22.04
- python: 3.10

```py:machine_cfg.py
# This Python script contains all the machine dependent settings
# needed during the build process.


# Compilers to be used.
cc              = "gcc"
cxx             = "g++"
f77             = "gfortran"
link            = 'gcc'

# Compiler flags.
flags           = "-Wall -pipe -O2 -fno-strength-reduce -DCPU=core2" # chooose appropreate cpu here (e.g. athlon64 etc. "586" should work always

link_flags      = "-O2"

# Include directories. (boost and python)

include_dirs    = ["/usr/include/",
		   "/usr/include/boost/",
		   "/usr/include/boost/python/",
		   "/usr/include/python3.10/"]
                
# Library directories.(those are the libraries of the compiler, python and boost)

library_dirs    = ["/lib/", "/usr/lib/", "/usr/lib/python3.10/"]
		
# Library names.

libs            = [ "python3.10" ,"boost_python" ]

# Command to strip library of excess symbols.

dllsuffix       = ".so"
strip_command   = ""

# look -recursive- in the dir tree and save files in a -special- array of arrays

import os
import os.path

def find_all_files(path, name):
    filelist        = []
    full_path       = path+name+"/"
    all_files_dirs  = os.listdir(full_path)

    for n in all_files_dirs:
        if os.path.isfile(full_path+n):
            filelist.append(full_path+ n)
        elif os.path.isdir(full_path+n):
            find_all_files(path,name+"/"+n)

    doclist.append([name, filelist])

# all documentation

docpath	        = "/home/XXXXX/download/rodis/"
doclist         = []
docname         = "doc"

find_all_files(docpath, docname)

# add more extra files

extra_files     = doclist 

```

適当なdirectory に展開する。
```
mkdir ~dists
cd dists
tar xvf ~/Downloads/rodis.tar.gz
```
``` libboost_python310.so ``` がinstall されていたので```、libboost_python.so``` にリンクする
```
/usr/lib/x86_64-linux-gnu$ sudo ln -s libboost_python310.so libboost_python.so
```
rodis をビルドする。
```
cd ~/dists/rodis
python3 setup.py build
```

### バイナリ格子のRCWA解析

実行するためのpython入力ファイルtest01.pyは以下の通りです。
```py:test01.py
#!/usr/bin/env python
# coding: utf-8
# Reproduces Fig. 2 in Moharam, Grann, Pommet, and Gaylord, "Formulation for stable and
# efficient implementation of the rigorous coupled-wave analysis of binary gratings",
# J. Opt. Soc. Am. A 12(5), pp. 1068–1076, 1995 (doi:10.1364/JOSAA.12.001068)

import rodis
from math import pi
import numpy
import matplotlib.pyplot as plt
 
def moharam(theta_rad,phi_rad,psi_rad,wavelength,ambient,pitch,fillfactor,thicknesses,substrate,norders):
    # rodis data
    rodis.set_lambda(wavelength)        # wavelength
    rodis.set_N(norders)                # orders of diffraction
    rodis.set_alpha(theta_rad)          # angle of incidence
    rodis.set_delta(phi_rad)            # 0 for planar diffraction
    rodis.set_psi(psi_rad)              # polarization angle
 
    solutions = []
    width = fillfactor*pitch
    for d in thicknesses:
        binary = rodis.Slab( ambient(0.5*width) + substrate(width) + ambient(0.5*width) )
        incident = rodis.Slab( ambient(pitch) )
        transmission = rodis.Slab( substrate(pitch) )
        grating = rodis.Stack( incident(1.) + binary(d) + transmission(1.) )
        grating.calc()
        solutions.append(grating.diffr_eff().T(1))
    return solutions
 
 
def plot(depths,wavelength,multiplier,TEsolutions,TMsolutions,conicalsolutions):
    plt.plot(depths/wavelength, TEsolutions, 'b.-', \
                depths/wavelength, TMsolutions, 'r.-', \
                depths/wavelength, conicalsolutions, 'k.-', \
                )
    plt.xlabel('Normalized groove depth $d/\lambda$')
    plt.ylabel('Diffraction efficiency $DE_1$')
 
    plt.legend(('TE', 'TM', 'conical  $(\\phi = 30^\circ, \psi = 45^\circ)$'))
    plt.axis('tight')
    plt.ylim([0,1])
    if multiplier == 1:
        plt.title("First-order transmitted diffraction efficiency\n" + \
                    "$n_I = 1$, $n_{II} = 2.04$, $\\theta = 10^\circ$, $\\Lambda = \lambda_0$")
        plt.savefig("moharam1995_lambda_" + str(int(depths[-1]/wavelength)) + "lambda.png")
        plt.savefig("moharam1995_lambda_" + str(int(depths[-1]/wavelength)) + "lambda.svg")
    else:
        plt.title("First-order transmitted diffraction efficiency\n" + \
                    "$n_I = 1$, $n_{II} = 2.04$, $\\theta = 10^\circ$, $\\Lambda =$ " + \
                    str(multiplier) + "$\lambda_0$")
        plt.savefig("moharam1995_"+str(multiplier)+"lambda_" + str(int(depths[-1]/wavelength)) + "lambda.png")
        plt.savefig("moharam1995_"+str(multiplier)+"lambda_" + str(int(depths[-1]/wavelength)) + "lambda.svg")
    plt.show()
 
 
def main():
    wavelength = 1.55
    norders = 15
    theta = 10.*pi/180  # angle of incidence
    phi = 30.*pi/180    # 0 for planar diffraction
 
    psi = 45.*pi/180    # polarization angle
     
    ambient = rodis.Material(1.0)
    substrate = rodis.Material(2.04)
 
    multiplier = 1
    pitch = multiplier*wavelength
    fill = 0.5
     
    depths = numpy.linspace(0.,5.,100)*wavelength
 
    # TE (psi = pi/2)
    print("TE")
    TEsolutions = moharam(theta,0.,pi/2,wavelength,ambient,pitch,fill,depths,substrate,norders)
 
    # TM (psi = 0)
    print("TM")
    TMsolutions = moharam(theta,0.,0.,wavelength,ambient,pitch,fill,depths,substrate,norders)
 
    # Conical
    print("Conical: \t phi = %.1f \t psi = %.1f" % (phi*180/pi,psi*180/pi))
    conicalsolutions = moharam(theta,phi,psi,wavelength,ambient,pitch,fill,depths,substrate,norders)
 
    plot(depths,wavelength,multiplier,TEsolutions,TMsolutions,conicalsolutions)
 
 
if __name__ == "__main__":
    main()
```
実行するには以下のようにします。
```
python3 test01.py
```
test01.py の実行結果を以下にしめします。
![](/images/Moharam/moharam1995_lambda_5lambda.png)

つぎに条件を変更したtest02.pyとの差分をしめします。
```
$ diff test01.py test02.py 
72c72
<     depths = numpy.linspace(0.,5.,100)*wavelength
---
>     depths = numpy.linspace(45.,50.,100)*wavelength

```
test02.pyの実行結果を以下にしめします。
![](/images/Moharam/moharam1995_lambda_50lambda.png)

つぎに条件を変更したtest03.pyとの差分をしめします。
```$ diff test01.py test03.py 
68c68
<     multiplier = 1
---
>     multiplier = 10


```
test03.pyの実行結果を以下にしめします。
![](/images/Moharam/moharam1995_10lambda_5lambda.png)

最後に4つ目の、test04.pyとの差分をしめします。
```
$ diff test01.py test04.py
68c68
<     multiplier = 1
---
>     multiplier = 10
72c72
<     depths = numpy.linspace(0.,5.,100)*wavelength
---
>     depths = numpy.linspace(45.,50.,100)*wavelength

```
test04.pyの実行結果を以下にしめします。
![](/images/Moharam/moharam1995_10lambda_50lambda.png)
### まとめ
## 参考文献
- M. G. Moharam, E. B. Grann, D. A. Pommet, and T. K. Gaylord, “Formulation for stable and eﬃcient implementation of the rigorous coupled-wave analysis of binary gratings,” J. Opt. Soc. Am. A 12(5), pp. 1068–1076, 1995
