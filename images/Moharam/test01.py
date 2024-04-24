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
