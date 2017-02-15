from io import StringIO
from os import path
from glob import iglob
from etl import config
from etl.handlers import dir_lister


# Prepare directory params
_this_dir   = path.dirname(__file__)
_parent_dir = path.dirname(_this_dir)


def _run_and_validate(masks, out_param: str, list_files: bool, **conf):
    """Run the handler and validate its result."""
    # Read dir contents
    mask_list = masks if type(masks) is list else [masks]
    expected = set()
    for mask in mask_list:
        # Files only
        if list_files:
            expected |= {f for f in iglob(mask) if path.isfile(f)}
        # Dirs only
        else:
            expected |= {f for f in iglob(mask) if path.isdir(f)}

    # Instantiate and run the handler
    h = dir_lister.Handler()
    result = h.run(config.Config(conf))

    # Convert the text into a set
    result = set(line.rstrip('\r\n') for line in StringIO(result[out_param]))
    print(result)

    # Check the result
    assert result == expected


def test_list_files_single():
    """handlers.dir_lister: test listing files by single mask"""
    mask = path.join(_this_dir, 'test_*.py')
    _run_and_validate(mask, 'data', True, file_masks=mask, include_dirs=False)


def test_list_files_multiple():
    """handlers.dir_lister: test listing files by multiple masks"""
    masks = [
        path.join(_this_dir,   'test_*.py'),
        path.join(_parent_dir, 'test_*.py'),
        path.join(_parent_dir, '*.json'),
    ]
    _run_and_validate(masks, 'data', True, file_masks=masks, include_dirs=False)


def test_list_dirs_single():
    """handlers.dir_lister: test listing dirs by single mask"""
    mask = path.join(_parent_dir, 'test_*')
    _run_and_validate(mask, 'data', False, file_masks=mask, include_files=False)


def test_mask_param_substitution_single():
    """handlers.dir_lister: test single mask parameter substitution"""
    mask = path.join(_parent_dir, 'test_*')
    mask_p = path.join('{dir}', 'test_*')
    _run_and_validate(mask, 'data', True, file_masks=mask_p, dir=_parent_dir, include_dirs=False)


def test_mask_param_substitution_multiple():
    """handlers.dir_lister: test multiple mask parameter substitution"""
    masks = [
        path.join(_this_dir,   'test_*.py'),
        path.join(_parent_dir, 'test_*.py'),
        path.join(_parent_dir, '*.json'),
    ]
    masks_p = [
        path.join('{tdir}', 'test_*.py'),
        path.join('{pdir}', 'test_*.py'),
        path.join('{pdir}', '*.json'),
    ]
    _run_and_validate(masks, 'data', True, file_masks=masks_p, tdir=_this_dir, pdir=_parent_dir, include_dirs=False)


def test_output_param():
    """handlers.dir_lister: test output parameter mapping"""
    mask = path.join(_this_dir, 'test_*.py')
    _run_and_validate(mask, 'OUT', True, file_masks=mask, include_dirs=False, output_param='OUT')
