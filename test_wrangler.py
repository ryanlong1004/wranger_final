"""tests"""
import json
import os
import yaml

from wrangler import LuaTranslator, Script

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root

SAMPLE_1 = """
test_1_eobsss:
    help: Load environment to run eobs job on WCOSS2
    whatis: eobs run environment
    content: 
      - modules:
        - cray-mpich/${cray_mpich_ver}
        - cray-pals/${cray_pals_ver}     
test_1_preppp:
    help: Load environment to run prep job on WCOSS2
    whatis: prep run environment
    content:
      - modules:
        - hdf5/${hdf5_ver}
        - python/${python_ver}
        - netcdf/${netcdf_ver}
        - crtm/${crtm_ver}
"""

SAMPLE_2 = """
^pre: &pre
  - modulepaths:
      - 1st
    modules:
      - 1PrgEnv-intel/${PrgEnv_intel_ver}
  - modulepaths:
      - 2nd
    modules:
      - 2PrgEnv-intel/${PrgEnv_intel_ver}
^post: &post
  - modulepaths:
      - None
    modules:
      - prod_util/${prod_util_ver}
test4:
    help: Load environment to run prep job on WCOSS2
    whatis: prep run environment
    content: 
      - <<: *pre
      - modulepaths:
          - None
        modules:
          - hdf5/${hdf5_ver}
          - python/${python_ver}
          - netcdf/${netcdf_ver}
          - crtm/${crtm_ver}
      - modulepaths:
          - "/extra1/lfs/h2/emc/global/save/emc.global/git/prepobs/module"
        modules:
          - extra1/${prepobs_ver}
          - extra1/${prepobs_ver}
          - extra1/${prepobs_ver}
        environment:
          - a: extra1
          - b: extra1
      - modulepaths:
          - "/extra2/lfs/h2/emc/global/save/emc.global/git/prepobs/module"
        modules:
          - extra2/${prepobs_ver}
          - extra2/${prepobs_ver}
          - extra2/${prepobs_ver}
        environment:
          - a: extra2
          - b: extra2
      - <<: *post
"""

ENV_VARS = {
    "PrgEnv_intel_ver": "1",
    "craype_ver": "2",
    "intel_ver": "3",
    "prod_util_ver": "4",
    "cray_mpich_ver": "5",
    "cray_pals_ver": "6",
    "python_ver": "7",
    "hdf5_ver": "8",
    "crtm_ver": "9",
    "netcdf_ver": "10",
    "prepobs_ver": "11",
}


def test_run_sample_1():
    translator = LuaTranslator()
    queue = (
        Script(script_name, data, translator)
        for (script_name, data) in yaml.safe_load(SAMPLE_1).items()
        if "^" not in script_name
    )

    expected = [
        {
            "name": "test_1_eobsss",
            "data": {
                "help": "Load environment to run eobs job on WCOSS2",
                "whatis": "eobs run environment",
                "content": [
                    {
                        "modules": [
                            "cray-mpich/${cray_mpich_ver}",
                            "cray-pals/${cray_pals_ver}",
                        ]
                    }
                ],
            },
        },
        {
            "name": "test_1_preppp",
            "data": {
                "help": "Load environment to run prep job on WCOSS2",
                "whatis": "prep run environment",
                "content": [
                    {
                        "modules": [
                            "hdf5/${hdf5_ver}",
                            "python/${python_ver}",
                            "netcdf/${netcdf_ver}",
                            "crtm/${crtm_ver}",
                        ]
                    }
                ],
            },
        },
    ]

    for idx, script in enumerate(queue):
        actual = repr(script)
        assert json.dumps(expected[idx]) == actual


def test_run_sample_2():
    translator = LuaTranslator()
    queue = (
        Script(script_name, data, translator)
        for (script_name, data) in yaml.safe_load(SAMPLE_2).items()
        if "^" not in script_name
    )

    expected = [
        {
            "name": "test4",
            "data": {
                "help": "Load environment to run prep job on WCOSS2",
                "whatis": "prep run environment",
                "content": [
                    {
                        "modulepaths": ["1st"],
                        "modules": ["1PrgEnv-intel/${PrgEnv_intel_ver}"],
                    },
                    {
                        "modulepaths": ["None"],
                        "modules": [
                            "hdf5/${hdf5_ver}",
                            "python/${python_ver}",
                            "netcdf/${netcdf_ver}",
                            "crtm/${crtm_ver}",
                        ],
                    },
                    {
                        "modulepaths": [
                            "/extra1/lfs/h2/emc/global/save/emc.global/git/prepobs/module"
                        ],
                        "modules": [
                            "extra1/${prepobs_ver}",
                            "extra1/${prepobs_ver}",
                            "extra1/${prepobs_ver}",
                        ],
                        "environment": [{"a": "extra1"}, {"b": "extra1"}],
                    },
                    {
                        "modulepaths": [
                            "/extra2/lfs/h2/emc/global/save/emc.global/git/prepobs/module"
                        ],
                        "modules": [
                            "extra2/${prepobs_ver}",
                            "extra2/${prepobs_ver}",
                            "extra2/${prepobs_ver}",
                        ],
                        "environment": [{"a": "extra2"}, {"b": "extra2"}],
                    },
                    {
                        "modulepaths": ["None"],
                        "modules": ["prod_util/${prod_util_ver}"],
                    },
                ],
            },
        }
    ]

    for idx, script in enumerate(queue):
        actual = repr(script)
        print(actual)
        assert json.dumps(expected[idx]) == actual
