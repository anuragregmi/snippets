# Management command that runs taks in background

## Usage

### Run workers
```sh
./manage.py runtasks
```

### Run task in background
```py3
from .utils import run_in_background

run_in_background('module.fn_name', 'arg1', kwarg='kwarg1')
```

