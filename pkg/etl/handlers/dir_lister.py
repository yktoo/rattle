import glob
import os
from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Lists the contents of a directory and returns it as list of file/dir names.

    Relevant configuration entries:
        file_masks    -- Full path to the directory, including file name mask, e.g. '/tmp/*.txt', or an array of such
                         paths. Can contain references to configuration parameters in the form '{param_name}'.
        include_files -- Boolean. Whether to include files. Optional, default is True.
        include_dirs  -- Boolean. Whether to include directories. Optional, default is True.
        output_param  -- Name of the parameter used for returning result data. Optional, default is 'data'.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        file_masks    = config['file_masks']
        include_files = bool(config['include_files', True])
        include_dirs  = bool(config['include_dirs',  True])
        output_param  = config['output_param', 'data']

        # Sanity check
        if not include_files and not include_dirs:
            logger.warning('Both "include_files" and "include_dirs" are false, the output will be null.')

        # Prepare mask(s). If a single mask is given, transform it into a single-element list
        if type(file_masks) is not list:
            file_masks = [file_masks]

        # Iterate through defined masks
        file_set = set()
        for file_mask in file_masks:
            # Substitute config params and canonicalise
            file_mask = context.get_absolute_file_name(file_mask.format(**config))

            # Append items matching the file mask
            file_set |= {
                fn for fn in glob.iglob(file_mask)
                if (include_files and os.path.isfile(fn)) or (include_dirs and os.path.isdir(fn))
            }

        # Return the result
        logger.info('Done. {} files/dirs are found.'.format(len(file_set)))
        return {output_param: '\n'.join(file_set) + '\n'}
