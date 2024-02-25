# umu
A Pip-style Package Manager for c++!

## Is this ready to use?
No. More work has to be done before this is ready for beta builds.

Only the download/install works right now, packages must be uninstalled and updated manually.
No download server exists yet either, so you must create the package configs yourself.

If you need this package, consider contributing to the project.

## Motivation

C++'s package management tools have long been clunky (environment variables), difficult to learn (cmake) or proprietary+buggy (NuGet). This is far removed from the smooth pipeline of package managers like pip.

umu aims to close the ease of use gap between python and c++ and allow easier building and installation for both editors and automated build pipelines.

As a result, umu should be a small and simple to use executable that is easy to integrate into most build systems.

## Example usage

### Creating an umuenv:

Navigate to the root folder of your solution and run:
```
umu umuenv
```

### Activating the umuenv:

From the root folder of your solution:
```
umuenv activate.bat
```

### Installing dependencies:
```
umu install <my-dependency>
```
or
```
umu install <my-dependency>==1.0.1
```

### Installing a requirements.umu
```
umu install -r requirements.umu
```
requirements.umu follows a requirements.txt format

## Build tool integration

### Visual Studio

In Project>C/C++>Additional Include Directories, add:
$(SolutionDir)\umuenv\include 

In Project>Linker>Additional Library Directories, add:
$(SolutionDir)\umuenv\libs 

Then add your headers like so:
#include <visual-leak-detector/vld.h>

Always match the include with the umu package name, even if their repo says otherwise!

### Other build tools

You'll have to figure it out, if you do please submit a pull request to update the documentation!

As a general rule:
- umu exposes the %UMU_HEADERS% and the %UMU_LIBS% environment variables. You can use these to include the libraries you need

## How does it work?

umu downloads the required packages to its central folder and then hardlinks/symlinks the include folders and library folders into the umuenv. From there your compiler should be able to access it.

Note: Hardlinks are used by default, but these do not work across different disk drives. In that case, the system falls back to Symlinks; which require administrator permission.

## Contributing

This isn't finished yet, so I'd much appreciate the help! Above shows roughly how I want the package to work, so if you see a place where you can jump in, go ahead!

### Testing
1. Install all the requirements
1. Create & activate the umuenv (haven't done that yet)
1. Run python zip_server.py
1. Run python install.py


