# Installation

__Pythons__: Python 3.4, 3.5, 3.6, 3.7

__Platforms__: Unix/Posix and Windows

## Prerequisites

* `Java 8`
* `GraphWalker CLI`
* `.NET Core` - optional

### GraphWalker

Altwalker relies on [Graphwalker](http://graphwalker.github.io/) to generate paths through your model(s).

AltWalker uses the GraphWalker CLI, the CLI is a standalone jar file. You need to have Java 8 installed to be able to execute the jar file.

You need to download [GraphWalker CLI](http://graphwalker.github.io/download/) and create a script to run the jar file from the command line.
We recomand downloading the latest version of GraphWalker CLI.

For macOS/linux you can run the following command:

```bash
$ wget https://github.com/GraphWalker/graphwalker-project/releases/download/LATEST-BUILDS/graphwalker-cli-4.0.0-SNAPSHOT.jar && \
  cp graphwalker-cli-4.0.0-SNAPSHOT.jar / && \
  echo '#!/bin/bash\njava -jar /graphwalker-cli-4.0.0-SNAPSHOT.jar "$@"' >> /graphwalker-cli && \
  chmod 777 /graphwalker-cli && \
  ln -s /graphwalker-cli /usr/bin/gw
```

Here is a more detailed [tutorial](http://graphwalker.github.io/cli-overview/#creating-a-script-facilitating-command-line-handling-on-a-linux-machine) for macOS/linux.

For windows you can run the following cmd commands:

```
$ setx PATH "%PATH%;C:\graphwalker" & :: Adds graphwalker to current user PATH
  cd C:\
  mkdir graphwalker
  cd graphwalker
  powershell -Command "[Net.ServicePointManager]::SecurityProtocol = 'tls12'; Invoke-WebRequest -Uri 'https://github.com/GraphWalker/graphwalker-project/releases/download/LATEST-BUILDS/graphwalker-cli-4.0.0-SNAPSHOT.jar' -outfile 'graphwalker-cli-4.0.0-SNAPSHOT.jar'" & :: Downloads graphwalker using powershell command Invoke-Request
  @echo off
  @echo @echo off> gw.bat
  @echo java -jar C:\graphwalker\graphwalker-cli-4.0.0-SNAPSHOT.jar %*>> gw.bat
  @echo on
```

After installing GraphWalker check that you installed the correct version:

```
$ gw --version
org.graphwalker version: 4.0.0-SNAPSHOT-58b6659

org.graphwalker is open source software licensed under MIT license
The software (and it's source) can be downloaded from http://graphwalker.org
For a complete list of this package software dependencies, see http://graphwalker.org/archive/site/graphwalker-cli/dependencies.html
```

Currently the latest version is `4.0.0-SNAPSHOT-58b6659`.

## Install `altwalker`

Run the following command in your command line:

```
$ pip install altwalker
```

Check that you installed the correct version:

```
$ altwalker --version
```


## Install .NET Core (Optional)

.NET Core is required by AltWalker when you want to write your tests in a dotnet supported language.  

* Install .NET Core Runtime - enables AltWalker to execute compiled tests. Preferred in production environment
* Install .NET Core SDK -  enables AltWalker to use dotnet to compile and run your tests. Preferred in development environment

dotnet command needs to be available under `/usr/bin/dotnet`. Installing .NET Core with snap makes the `dotnet` command available under a different path. In this case create a symbolic link `ln -s /path/to/dotnet /usr/bin/dotnet` 