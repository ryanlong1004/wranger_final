"""tests"""
import json
import os
from pathlib import Path
import yaml

from wrangler import LuaTranslator, Script, write_scripts_to_files

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

SAMPLE_3 = """
^pre: &pre
  - modulepaths:
      - None
    modules:
      - PrgEnv-intel/${PrgEnv_intel_ver}
^post: &post
  - modulepaths:
      - None
    modules:
      - prod_util/${prod_util_ver}
prep:
  help: Load environment to run prep job on WCOSS2
  whatis: prep run environment
  content:
    - <<: *pre
    - modulepaths:
      - None
      modules:
      - hdf5
      - python/3.8.5
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
    """Sample 1"""
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

    expected_content = [
        [
            'load(pathJoin("cray-mpich", "os.getenv(cray_mpich_ver)"))\n',
            'load(pathJoin("cray-pals", "os.getenv(cray_pals_ver)"))\n',
        ],
        [
            'load(pathJoin("hdf5", "os.getenv(hdf5_ver)"))\n',
            'load(pathJoin("python", "os.getenv(python_ver)"))\n',
            'load(pathJoin("netcdf", "os.getenv(netcdf_ver)"))\n',
            'load(pathJoin("crtm", "os.getenv(crtm_ver)"))\n',
        ],
    ]

    for idx, script in enumerate(queue):
        actual = repr(script)
        assert json.dumps(expected[idx]) == actual

        print("*" * 10)
        print(script.content)
        print("*" * 10)
        print(expected_content[idx])
        print("*" * 10)
        assert script.content == expected_content[idx]


def test_run_sample_2():
    """Sample 2"""
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
        assert json.dumps(expected[idx]) == actual

        expected = [
            'prepend_path("MODULEPATH", pathJoin("1st"))\n',
            'load(pathJoin("1PrgEnv-intel", "os.getenv(PrgEnv_intel_ver)"))\n',
            'load(pathJoin("hdf5", "os.getenv(hdf5_ver)"))\n',
            'load(pathJoin("python", "os.getenv(python_ver)"))\n',
            'load(pathJoin("netcdf", "os.getenv(netcdf_ver)"))\n',
            'load(pathJoin("crtm", "os.getenv(crtm_ver)"))\n',
            'prepend_path("MODULEPATH", pathJoin("/extra1/lfs/h2/emc/global/save/emc.global/git/prepobs/module"))\n',
            'load(pathJoin("extra1", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra1", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra1", "os.getenv(prepobs_ver)"))\n',
            'setenv("a", "extra1")\n',
            'setenv("b", "extra1")\n',
            'prepend_path("MODULEPATH", pathJoin("/extra2/lfs/h2/emc/global/save/emc.global/git/prepobs/module"))\n',
            'load(pathJoin("extra2", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra2", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra2", "os.getenv(prepobs_ver)"))\n',
            'setenv("a", "extra2")\n',
            'setenv("b", "extra2")\n',
            'load(pathJoin("prod_util", "os.getenv(prod_util_ver)"))\n',
        ]
        assert script.content == expected


def test_run_sample_3():
    """Sample 3"""
    translator = LuaTranslator()
    queue = (
        Script(script_name, data, translator)
        for (script_name, data) in yaml.safe_load(SAMPLE_3).items()
        if "^" not in script_name
    )

    expected = [
        {
            "name": "prep",
            "data": {
                "help": "Load environment to run prep job on WCOSS2",
                "whatis": "prep run environment",
                "content": [
                    {
                        "modulepaths": ["None"],
                        "modules": ["PrgEnv-intel/${PrgEnv_intel_ver}"],
                    },
                    {
                        "modulepaths": ["None"],
                        "modules": [
                            "hdf5",
                            "python/3.8.5",
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
        write_scripts_to_files([script], Path("./"))

        print(json.dumps(expected[idx]))
        # print(actual)
        assert json.dumps(expected[idx]) == actual

        expected = [
            'load(pathJoin("PrgEnv-intel", "os.getenv(PrgEnv_intel_ver)"))\n',
            'load(pathJoin("hdf5"))\n',
            'load(pathJoin("python", "3.8.5"))\n',
            'load(pathJoin("netcdf", "os.getenv(netcdf_ver)"))\n',
            'load(pathJoin("crtm", "os.getenv(crtm_ver)"))\n',
            'prepend_path("MODULEPATH", pathJoin("/extra1/lfs/h2/emc/global/save/emc.global/git/prepobs/module"))\n',
            'load(pathJoin("extra1", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra1", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra1", "os.getenv(prepobs_ver)"))\n',
            'setenv("a", "extra1")\n',
            'setenv("b", "extra1")\n',
            'prepend_path("MODULEPATH", pathJoin("/extra2/lfs/h2/emc/global/save/emc.global/git/prepobs/module"))\n',
            'load(pathJoin("extra2", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra2", "os.getenv(prepobs_ver)"))\n',
            'load(pathJoin("extra2", "os.getenv(prepobs_ver)"))\n',
            'setenv("a", "extra2")\n',
            'setenv("b", "extra2")\n',
            'load(pathJoin("prod_util", "os.getenv(prod_util_ver)"))\n',
        ]
        assert script.content == expected


if __name__ == "__main__":
    for idx, script in enumerate([SAMPLE_1, SAMPLE_2, SAMPLE_3]):
        with open(f"./{idx}.yaml", "w", encoding="utf-8") as _file:
            _file.write(script)
