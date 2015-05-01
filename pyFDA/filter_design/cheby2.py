# -*- coding: utf-8 -*-
"""
Created on Wed December 17 2014

Design cheby2-Filters (LP, HP, BP, BS) with fixed or minimum order, return
the filter design in zeros, poles, gain (zpk) format

@author: Christian Muenker

Expected changes in scipy 0.16:
https://github.com/scipy/scipy/pull/3717
https://github.com/scipy/scipy/issues/2444
"""
from __future__ import print_function, division, unicode_literals
import scipy.signal as sig
from scipy.signal import cheb2ord
import numpy as np
import pyfda_lib

frmt = 'ba' # output format of filter design routines 'zpk' / 'ba' / 'sos'

class cheby2(object):

    def __init__(self):

        self.name = {'cheby2':'Chebychev 2'}

        # common messages for all man. / min. filter order response types:
        msg_man = ("Enter the filter order <b><i>N</i></b>, the minimum stop band "
            "attenuation <b><i>A<sub>SB</sub></i></b>, and the frequency / "
            "frequencies <b><i>F<sub>SB</sub></i></b> where gain first drops "
            "below <b><i>A<sub>SB</sub></i></b>.")
        msg_min = ("Enter the maximum pass band ripple and minimum stop band "
                    "attenuation and the corresponding corner frequencies.")

        # enabled widgets for all man. / min. filter order response types:
        enb_man = ['fo','fspecs','aspecs'] # enabled widget for man. filt. order
        enb_min = ['fo','fspecs','aspecs'] # enabled widget for min. filt. order

        # common parameters for all man. / min. filter order response types:
        par_man = ['N', 'f_S', 'F_SB', 'A_SB'] # enabled widget for man. filt. order
        par_min = ['f_S', 'A_PB', 'A_SB'] # enabled widget for min. filt. order

        # Common data for all man. / min. filter order response types:
        # This data is merged with the entries for individual response types
        # (common data comes first):
        self.com = {"man":{"enb":enb_man, "msg":msg_man, "par": par_man},
                    "min":{"enb":enb_min, "msg":msg_min, "par": par_min}}

        self.ft = 'IIR'
        self.rt = {
          "LP": {"man":{"par":[]},
                 "min":{"par":['F_PB','F_SB']}},
          "HP": {"man":{"par":[]},
                 "min":{"par":['F_SB','F_PB']}},
          "BP": {"man":{"par":['F_SB2']},
                 "min":{"par":['F_SB','F_PB','F_PB2','F_SB2']}},
          "BS": {"man":{"par":['F_SB2']},
                 "min":{"par":['F_PB','F_SB','F_SB2','F_PB2']}}
                 }

        self.info = """
**Chebyshev Type 2 filters**

have a constant ripple :math:`A_SB` in the stop band(s) only, the pass band
drops monotonously. This is achieved by placing `N/2` zeros along the stop
band.

The order :math:`N`, stop band ripple :math:`A_SB` and
the critical frequency / frequencies F\ :sub:`SB` where the stop band attenuation
:math:`A_SB` is reached have to be specified for filter design.

The corner frequency/ies of the pass band can only be controlled indirectly
by the filter order and by slightly adapting the value(s) of F\ :sub:`SB`.

**Design routines:**

``scipy.signal.cheby2()``
``scipy.signal.cheb2ord()``
"""

        self.info_doc = []
        self.info_doc.append('cheby2()\n========')
        self.info_doc.append(sig.cheby2.__doc__)
        self.info_doc.append('cheb2ord()\n==========')
        self.info_doc.append(sig.cheb2ord.__doc__)

    def get_params(self, fil_dict):
        """
        Translate parameters from the passed dictionary to instance
        parameters, scaling / transforming them if needed.
        """
        self.N     = fil_dict['N']
        self.F_PB  = fil_dict['F_PB'] * 2
        self.F_SB  = fil_dict['F_SB'] * 2
        self.F_PB2 = fil_dict['F_PB2'] * 2
        self.F_SB2 = fil_dict['F_SB2'] * 2
        self.F_SBC = None
        self.A_PB  = fil_dict['A_PB']
        self.A_SB  = fil_dict['A_SB']
        self.A_PB2 = fil_dict['A_PB2']
        self.A_SB2 = fil_dict['A_SB2']

    def save(self, fil_dict, arg):
        """
        Convert poles / zeros / gain to filter coefficients (polynomes) and the
        other way round
        """
        pyfda_lib.save_fil(fil_dict, arg, frmt, __name__)

        if self.F_SBC is not None: # has the order been calculated by a "min" filter design?
            fil_dict['N'] = self.N # yes, update filterbroker
            if np.isscalar(self.F_SBC): # HP or LP - a single corner frequency
                fil_dict['F_SB'] = self.F_SBC / 2.
            else: # BP or BS - two corner frequencies
                fil_dict['F_SB'] = self.F_SBC[0] / 2.
                fil_dict['F_SB2'] = self.F_SBC[1] / 2.

    def LPman(self, fil_dict):
        self.get_params(fil_dict)
        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, self.F_SB,
                              btype='low', analog = False, output = frmt))
    # LP: F_PB < F_SB
    def LPmin(self, fil_dict):
        self.get_params(fil_dict)
        self.N, self.F_SBC = cheb2ord(self.F_PB,self.F_SB, self.A_PB,self.A_SB)
        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, self.F_SBC,
                            btype='lowpass', analog = False, output = frmt))
#        self.save(fil_dict, iirdesign(self.F_PB, self.F_SB, self.A_PB, self.A_SB,
#                             analog=False, ftype='cheby2', output=frmt))

    def HPman(self, fil_dict):
        self.get_params(fil_dict)
        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, self.F_SB,
                            btype='highpass', analog = False, output = frmt))

    # HP: F_SB < F_PB
    def HPmin(self, fil_dict):
        self.get_params(fil_dict)
        self.N, self.F_SBC = cheb2ord(self.F_PB, self.F_SB,self.A_PB,self.A_SB)
        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, self.F_SBC,
                            btype='highpass', analog = False, output = frmt))



    # For BP and BS, A_PB, A_SB, F_PB and F_SB have two elements each
    def BPman(self, fil_dict):
        self.get_params(fil_dict)
        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, [self.F_SB, self.F_SB2],
                            btype='bandpass', analog = False, output = frmt))

    # BP: F_SB[0] < F_PB[0], F_SB[1] > F_PB[1]
    def BPmin(self, fil_dict):
        self.get_params(fil_dict)
        self.N, self.F_SBC = cheb2ord([self.F_PB, self.F_PB2],
                                [self.F_SB, self.F_SB2], self.A_PB, self.A_SB)

        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, self.F_SBC,
                            btype='bandpass', analog = False, output = frmt))
#        self.save(fil_dict, iirdesign([self.F_PB,self.F_PB2],
#                [self.F_SB, self.F_SB2], self.A_PB, self.A_SB,
#                             analog=False, ftype='cheby2', output=frmt))

    def BSman(self, fil_dict):
        self.get_params(fil_dict)
        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, [self.F_SB, self.F_SB2],
                        btype='bandstop', analog = False, output = frmt))

    # BS: F_SB[0] > F_PB[0], F_SB[1] < F_PB[1]
    def BSmin(self, fil_dict):
        self.get_params(fil_dict)
        self.N, self.F_SBC = cheb2ord([self.F_PB, self.F_PB2],
                                [self.F_SB, self.F_SB2], self.A_PB, self.A_SB)

        self.save(fil_dict, sig.cheby2(self.N, self.A_SB, self.F_SBC,
                            btype='bandstop', analog = False, output = frmt))
