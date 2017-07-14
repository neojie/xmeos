import numpy as np
import scipy as sp
from abc import ABCMeta, abstractmethod

#====================================================================
# Base EOS Model Class
#====================================================================
class EosMod(object):
    """
    Abstract Equation of State Parent Base class
    """
    __metaclass__ = ABCMeta

    def __init__( self ):
        pass

    def get_param_scale( self, eos_d, apply_expand_adj=True):
        """Return scale values for each parameter"""
        return self.get_param_scale_sub( eos_d )

    def get_param_scale_sub( self, eos_d ):
        raise NotImplementedError("'get_param_scale_sub' function not implimented for this model")
#====================================================================

#====================================================================
def init_consts( eos_d ):
    eos_d['const_d'] = default_consts()
    pass
#====================================================================
def default_consts():
    const_d = {}
    const_d['eVperHa'] = 27.211 # eV/Ha
    const_d['JperHa'] = 4.35974434e-18 # J/Ha
    const_d['JperCal'] = 4.184 # J/Cal
    const_d['Nmol'] = 6.0221413e+23 # atoms/mol
    const_d['kJ_molpereV'] = 96.49 # kJ/mol/eV
    const_d['R'] = 8.314462 # J/K/mol
    const_d['kboltz'] = 8.617332e-5 # eV/K
    const_d['ang3percc'] = 1e24 # ang^3/cm^3

    const_d['PV_ratio'] = 160.2176487 # (GPa*ang^3)/eV
    const_d['TS_ratio'] = const_d['R']/const_d['kboltz'] # (J/mol)/eV

    return const_d
#====================================================================
def set_consts( name_l, val_l, eos_d ):
    if 'const_d' in eos_d.keys():
        const_d = eos_d['const_d']
    else:
        init_consts( eos_d )

    for name, val in zip( name_l, val_l ):
        const_d[name] = val

    pass
#====================================================================
def get_consts( name_l, eos_d ):
    """
    Retrieve list of desired consts stored in eos_d['const_d']
    """
    const_d = eos_d['const_d']
    const_l = []
    for name in name_l:
        const_l.append( const_d[name] )

    return tuple( const_l )
#====================================================================
def set_params( name_l, val_l, eos_d ):
    if 'param_d' in eos_d.keys():
        param_d = eos_d['param_d']
    else:
        param_d = {}
        eos_d['param_d'] = param_d

    for name, val in zip( name_l, val_l ):
        param_d[name] = val

    pass
#====================================================================
def get_params( name_l, eos_d ):
    """
    Retrieve list of desired params stored in eos_d['param_d']
    """
    param_d = eos_d['param_d']
    param_l = []
    for name in name_l:
        param_l.append( param_d[name] )

    return tuple( param_l )
#====================================================================
def swap_params( name_l, eos_d ):
    """
    Retrieve list of desired params stored in eos_d['param_d']
    """

    # Use shallow copy to avoid unneeded duplication
    eos_swap_d = copy.copy( eos_d )
    # Use deep copy on params to ensure swap without affecting original
    param_swap_d = copy.deepcopy(eos_d['param_d'])

    eos_swap_d['param_d'] = param_swap_d

    set_params( name_l, eos_swap_d )

    return eos_swap_d
#====================================================================
def set_array_params( basename, param_arr_a, eos_d ):
    name_l = []

    for i in range(len(param_arr_a)):
        iname = basename+'_'+np.str(i)
        name_l.append(iname)

    set_params(name_l, param_arr_a, eos_d)
#====================================================================
def get_array_params( basename, eos_d ):
    param_d = eos_d['param_d']
    paramkeys_a = np.array(param_d.keys())

    baselen = len(basename+'_')

    mask = np.array([key.startswith(basename+'_') for key in paramkeys_a])

    arrindlist = []
    vallist = []
    for key in paramkeys_a[mask]:
        idstr = key[baselen:]
        try:
            idnum = np.array(idstr).astype(np.float)
            assert np.equal(np.mod(idnum,1),0), \
                'Parameter keys that are part of a parameter array must '+\
                'have form "basename_???" where ??? are integers.'
            idnum = idnum.astype(np.int)
        except:
            assert False, 'That basename does not correspond to any valid parameter arrays stored in eos_d'

        arrindlist.append(idnum)
        vallist.append(param_d[key])

    arrind_a = np.array(arrindlist)
    val_a = np.array(vallist)

    if arrind_a.size==0:
        return np.array([])
    else:
        indmax = np.max(arrind_a)

        param_arr = np.zeros(indmax+1)
        for arrind, val in zip(arrind_a,val_a):
            param_arr[arrind] = val

        return param_arr
#====================================================================
def set_modtypes( name_l, val_l, eos_d ):
    if 'modtype_d' in eos_d.keys():
        modtype_d = eos_d['modtype_d']
    else:
        modtype_d = {}
        eos_d['modtype_d'] = modtype_d

    # Should we verify match?
    for name, val in zip( name_l, val_l ):
        modtype_d[name] = val
        # No longer functional test
        # if globals().has_key(name):
        #     # modtype = globals()[name]
        #     # modtype_d[name] = modtype()
        #     modtype_d[name] = val
        # else:
        #     print name + " is not a valid modtype object"

    pass
#====================================================================
def get_modtypes( name_l, eos_d ):
    """
    Retrieve list of desired model types stored in eos_d['modtype_d']
    """
    modtype_d = eos_d['modtype_d']
    modtype_l = []
    for name in name_l:
        modtype_l.append( modtype_d[name] )

    return tuple( modtype_l )
#====================================================================
def set_args( name_l, val_l, eos_d ):
    if 'arg_d' in eos_d.keys():
        arg_d = eos_d['arg_d']
    else:
        arg_d = {}
        eos_d['arg_d'] = arg_d

    for name, val in zip( name_l, val_l ):
        arg_d[name] = val

    pass
#====================================================================
def fill_array( var1, var2 ):
    """
    fix fill_array such that it returns two numpy arrays of equal size

    use numpy.full_like

    """
    var1_a = np.asarray( var1 )
    var2_a = np.asarray( var2 )

    if var1_a.shape==():
        var1_a = np.asarray( [var1] )
    if var2_a.shape==():
        var2_a = np.asarray( [var2] )

    # Begin try/except block to handle all cases for filling an array
    while True:
        try:
            assert var1_a.shape == var2_a.shape
            break
        except: pass
        try:
            var1_a = np.full_like( var2_a, var1_a )
            break
        except: pass
        try:
            var2_a = np.full_like( var1_a, var2_a )
            break
        except: pass

        # If none of the cases properly handle it, throw error
        assert False, 'var1 and var2 must both be equal shape or size=1'

    return var1_a, var2_a
#====================================================================

#====================================================================
# ModFit Class (Is this even in use?)
#====================================================================
class ModFit(object):
    def __init__( self ):
        pass

    def get_resid_fun( self, eos_fun, eos_d, param_key_a, sys_state_tup,
                      val_a, err_a=1.0):

        # def resid_fun( param_in_a, eos_fun=eos_fun, eos_d=eos_d,
        #               param_key_a=param_key_a, sys_state_tup=sys_state_tup,
        #               val_a=val_a, err_a=err_a ):

        #     # Don't worry about transformations right now
        #     param_a = param_in_a

        #     # set param value in eos_d dict
        #     globals()['set_param']( param_key_a, param_a, eos_d )

        #     # Take advantage of eos model function input format
        #     #   uses tuple expansion for input arguments
        #     mod_val_a = eos_fun( *(sys_state_tup+(eos_d,)) )
        #     resid_a = (mod_val_a - val_a)/err_a
        #     return resid_a

        wrap_eos_fun = self.get_wrap_eos_fun( eos_fun, eos_d, param_key_a )

        def resid_fun( param_in_a, wrap_eos_fun=wrap_eos_fun,
                      sys_state_tup=sys_state_tup,
                      val_a=val_a, err_a=err_a ):

            mod_val_a = wrap_eos_fun( param_in_a, sys_state_tup )
            resid_a = (mod_val_a - val_a)/err_a
            return resid_a

        return resid_fun

    def get_wrap_eos_fun( self, eos_fun, eos_d, param_key_a ):

        def wrap_eos_fun(param_in_a, sys_state_tup, eos_fun=eos_fun,
                         eos_d=eos_d, param_key_a=param_key_a ):

            # Don't worry about transformations right now
            param_a = param_in_a

            # set param value in eos_d dict
            Control.set_params( param_key_a, param_a, eos_d )

            # Take advantage of eos model function input format
            #   uses tuple expansion for input arguments
            mod_val_a = eos_fun( *(sys_state_tup+(eos_d,)) )
            return mod_val_a

        return wrap_eos_fun
#====================================================================
