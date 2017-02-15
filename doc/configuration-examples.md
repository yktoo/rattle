# Configuration examples

A very simple [configuration file](configuration-file-format.md) shown below makes the ETL tool list directories in the `/home` folder and save the list into the file `USERLIST.txt`. It demonstrates the basic concepts Rattle implements.

```json
{
    "log": {
        "verbose": true
    },
    "processes": [
        {
            "name": "Test",
            "comment": "Testing stuff",
            "handler": [
                {
                    "module": "dir_lister",
                    "file_masks": "/home/*",
                    "include_files": false,
                    "include_dirs": true,
                    "output_param": "user_list"
                },
                {
                    "module": "file_writer",
                    "input_param": "user_list",
                    "output_file": "USERLIST.txt"
                }
            ]
        }
    ]
}
```
