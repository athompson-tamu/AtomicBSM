"""
Class for setting and getting crystal parameters, lattice vectors, and structure functions
"""

from .constants import *
from .math_helper import *
import json
import pkg_resources




# Class to hold detector-specific constants, dimensions, and responses
class Detector:
    """
    detector class
    """
    def __init__(self, det_type, fiducial_mass=1.0, volume=1.0, density=1.0, efficiency=None):
        """
        initializing Detector,
        it reads ./det_params.json for detector information,
        :param det_type: name of the detector
        all units in MeV, kg, cm, unless otherwise stated (e.g. lattice params)
        """
        self.det_type = det_type
        self.efficiency = efficiency
        fpath = pkg_resources.resource_filename(__name__, '../data/det_params.json')
        f = open(fpath, 'r')
        det_file = json.load(f)
        f.close()
        if det_type.lower() in det_file:
            det_info = det_file[det_type.lower()]
            self.iso = det_info['iso']
            self.z = np.array(det_info['z'])
            self.n = np.array(det_info['n'])
            self.m = np.array(det_info['m'])
            self.frac = np.array(det_info['frac'])
            self.lattice_const = np.array([det_info['lattice_const']])  # Angstroms
            self.cell_volume = np.array([det_info['cell_volume']])  # Angstroms^3
            self.r0 = np.array([det_info['atomic_radius']])  # Angstroms
            self.er_min = det_info['er_min']
            self.er_max = det_info['er_max']
            self.bg = det_info['bg']
            self.bg_un = det_info['bg_un']
            self.fid_mass = fiducial_mass  # kg
            self.volume = volume  # cm^3
            self.density = density  # g/cm^3
        else:
            raise Exception("No such detector in det_params.json.")



"""
lattice_const: lattice constant in Angstroms
primitives: an array of the N primitive basis vectors in format [alpha0, alpha1,...]
        for each alpha = [#,#,#] as a 3-list
a1, a2, a3: Bravais lattice vectors as 3-lists [#,#,#]
"""
class Crystal(Detector):
    def __init__(self, material, primitives, a1, a2, a3, volume=1.0, density=1.0,
                fiducial_mass=1.0):
        super().__init__(det_type=material, fiducial_mass=fiducial_mass, volume=volume, density=density)
        self.a = self.lattice_const[0]
        self.alpha = self.a * np.array(primitives)
        self.a0 = self.a * np.array([0,0,0])
        self.a1 = self.a * np.array(a1)
        self.a2 = self.a * np.array(a2)
        self.a3 = self.a * np.array(a3)
        self.basis = np.array([self.a0, self.a1, self.a2, self.a3])

        self.b1 = 2*pi*cross(self.a2, self.a3) / (dot(self.a1, cross(self.a2, self.a3)))
        self.b2 = 2*pi*cross(self.a3, self.a1) / (dot(self.a1, cross(self.a2, self.a3)))
        self.b3 = 2*pi*cross(self.a1, self.a2) / (dot(self.a1, cross(self.a2, self.a3)))
    
    def r(self, n1, n2, n3):
        return n1 * self.a1 + n2 * self.a2 + n3 * self.a3
    
    def G(self, h, k, l):
        return h * self.b1 + k * self.b2 + l * self.b3
    
    def wavelength(self, h, k, l):
        return 2*pi/sqrt(dot(self.G(h, k, l), self.G(h, k, l)))
    
    def energy(self, h, k, l):
        return HBARC * sqrt(dot(self.G(h, k, l), self.G(h, k, l)))
    
    def miller(self, h, k, l):
        return np.array([h, k, l])
    
    def sfunc(self, h, k, l):
        return abs((1+exp(-1j * dot(self.alpha[1], self.G(h, k, l)))) \
            * sum([exp(-2*pi*1j*dot(self.miller(h, k, l), avec/self.a)) for avec in self.basis]))



# Namelist
cryslist = ["Ge", "Si", "NaI", "CsI"]


def get_crystal(name):
    if name not in cryslist:
        print("Specified material not in library. Supported crystals:\n", cryslist)
        return
    
    if name == "Ge":
        # Diamond cubic, germanium
        GeAlpha0 = [0.0, 0.0, 0.0]
        GeAlpha1 = [0.25, 0.25, 0.25]
        Primitives = [GeAlpha0, GeAlpha1]
        A1 = [0.0, 0.5, 0.5]
        A2 = [0.5, 0.0, 0.5]
        A3 = [0.5, 0.5, 0.0]
        return Crystal(name, Primitives, A1, A2, A3)
    
    if name == "Si":
        pass
    
    if name == "NaI":
        # Diamond cubic, sodium iodide
        Alpha0 = [0.0, 0.0, 0.0]
        Alpha1 = [0.5, 0.5, 0.5]
        Primitives = [Alpha0, Alpha1]
        A1 = [0.0, 0.5, 0.5]
        A2 = [0.5, 0.0, 0.5]
        A3 = [0.5, 0.5, 0.0]
        return Crystal(name, Primitives, A1, A2, A3)

    if name == "CsI":
        pass

    return