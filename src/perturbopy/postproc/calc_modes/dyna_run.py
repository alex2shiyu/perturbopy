import numpy as np
import os
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.calc_modes.dyna_indiv_run import DynaIndivRun
from perturbopy.io_utils.io import open_yaml, open_hdf5, close_hdf5
from perturbopy.postproc.utils.timing import Timing, TimingGroup
from perturbopy.postproc.dbs.units_dict import UnitsDict

class DynaRun(CalcMode):
    """
    Class representation of a Perturbo dynamics-run calculation.

    Attributes
    ----------
    kpt : RecipPtDB
       Database for the k-points used in the bands calculation.
    bands : UnitsDict
       Database for the band energies computed by the bands calculation.
    num_runs : int
        Number of separate simulations performed
    _dat : dict
        Python dictionary of DynaIndivRun objects containing results from each simulation
    """

    def __init__(self, cdyna_file, tet_file, pert_dict):
        """
        Constructor method

        Parameters
        ----------
        pert_dict : dict
            Dictionary containing the inputs and outputs from the dynamics-run calculation.

        """
        
        self.timings = TimingGroup("dynamics-run")

        super().__init__(pert_dict)

        if self.calc_mode != 'dynamics-run':
            raise ValueError('Calculation mode for a DynamicsRunCalcMode object should be "dynamics-run"')

        kpoint = np.array(tet_file['kpts_all_crys_coord'][()])

        self.kpt = RecipPtDB.from_lattice(kpoint, "crystal", self.lat, self.recip_lat)
        self.bands = UnitsDict.from_dict

        energies = np.array(cdyna_file['band_structure_ryd'][()])
        energies_dict = {i + 1: np.array(energies[:, i]) for i in range(0, energies.shape[1])}
        self.bands = UnitsDict.from_dict(energies_dict, 'Ry')

        self._data = {}

        self.num_runs = cdyna_file['num_runs'][()]

        with self.timings.add('iterate_dyna') as t:

            for irun in range(1, self.num_runs + 1):
                dyn_str = f'dynamics_run_{irun}'

                num_steps = cdyna_file[dyn_str]['num_steps'][()]
                time_step = cdyna_file[dyn_str]['time_step_fs'][()]

                # a dynamics run must have at least one snap
                numk, numb = cdyna_file[dyn_str]['snap_t_1'][()].shape

                snap_t = np.zeros((numb, numk, num_steps), dtype=np.float64)

                for itime in range(num_steps):
                    snap_t[:, :, itime] = cdyna_file[dyn_str][f'snap_t_{itime+1}'][()].T

                # Get E-field, which is only present if nonzero
                if "efield" in cdyna_file[dyn_str].keys():
                    efield = cdyna_file[dyn_str]["efield"][()]
                else: 
                    efield = np.array([0.0, 0.0, 0.0])

                self._data[irun] = DynaIndivRun(num_steps, time_step, snap_t, time_units='fs', efield=efield)

    @classmethod
    def from_hdf5_yaml(cls, cdyna_path, tet_path, yaml_path='pert_output.yml'):
        """
        Class method to create a DynamicsRunCalcMode object from the HDF5 file and YAML file
        generated by a Perturbo calculation

        Parameters
        ----------
        cdyna_path : str
           Path to the HDF5 file generated by a dynamics-run calculation
        tet_path : str
           Path to the HDF5 file generated by the setup calculation required before the dynamics-run calculation
        yaml_path : str, optional
           Path to the YAML file generated by a dynamics-run calculation

        Returns
        -------
        dyanamics_run : DynamicsRunCalcMode
           The DynamicsRunCalcMode object generated from the HDF5 and YAML files

        """

        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')
        if not os.path.isfile(cdyna_path):
            raise FileNotFoundError(f'File {cdyna_path} not found')
        if not os.path.isfile(tet_path):
            raise FileNotFoundError(f'File {tet_path} not found')

        yaml_dict = open_yaml(yaml_path)
        cdyna_file = open_hdf5(cdyna_path)
        tet_file = open_hdf5(tet_path)

        return cls(cdyna_file, tet_file, yaml_dict)


    def __getitem__(self, index):
        """
        Method to index the DynamicsRunCalcMode object

        Parameters
        ----------
        index : int
            The dynamics run requested, indexing starting at 1

        Returns
        -------
        dynamics_run: DynamicsRun
           Object containing information for the dynamics run

        """
        if index <= 0 or index > len(self._data):
            raise IndexError("Index out of range")

        return self._data[index]

    def __len__(self):
        """
        Method to get the number of runs in DynamicsRunCalcMode object

        Returns
        -------
        num_runs : int
            Number of runs
        """

        return self.num_runs

    def get_info(self):
        """
        Method to get overall information on dynamics runs
        """

        print(f"\nThis simulation has {self.num_runs} runs")

        for irun, dynamics_run in self._data.items():

            print(f"{'Dynamics run':>30}: {irun}")
            print(f"{'Number of steps':>30}: {dynamics_run.num_steps}")
            print(f"{'Time step (fs)':>30}: {dynamics_run.time_step}")
            print(f"{'Electric field (V/cm)':>30}: {dynamics_run.efield}")
            print("")