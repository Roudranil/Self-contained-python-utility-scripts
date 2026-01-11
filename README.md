A collection of simple (but long) utility scripts that I use in my python projects

## descriptions

### logger.py

exposes a func `create_logger` which instantiates a logger with loguru and returns it.  
requres:
- loguru

### meminfo.py

exposes some functions to calculate ram and vram usage and delete variables from memory . the `clean_mem()` function is directly copied from the code as shown in Jeremy Howard's amazing youtube playlist [Practical Deep Learning Part 2](https://www.youtube.com/playlist?list=PLfYUBJiXbdtRUvTUYpLdfHHp9a58nWVXP) (highly recommended for anybody learning to get into diffusion models)

requires:
- loguru
- torch
- ipython

### torchsummary.py

exposes a single function `summary` that prints the summary of a pytorch model. It has slightly less capabilities and features but is more opinionated than [torchinfo.summary()](https://github.com/tyleryep/torchinfo). My function is heavily inspired by it.

requires:
- torch