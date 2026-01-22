# Code for IBM i

## Developing on the IFS with ibmi-tobi

1. Make sure `ibmi-tobi` is installed on the remote IBM i
2. Set your current schema to the library you want to build in. You can do this in the User Library List view.
3. Create a new Action
   * Give it a unique name. This action will attempt to build everything
   * **Command to run**: `OPT=*EVENTF BUILDLIB=&CURLIB /QOpenSys/pkgs/bin/makei build`
      * `&CURLIB` will be the current library you set in VS Code.
   * **Extensions**: `GLOBAL`
   * **Types**: Streamfile
   * **Environment**: `PASE`
4. In the IFS Browser: right-click on the project directory and select 'Change working directory'
5. Open the source code up that you want to compile
6. Use the Action, which will run the defined command
   * Shortcut to run an Action is Control / Command + E
   * You will see the Output in the IBM i Output channel.
   * If your current library and build library match, the errors (if any) should appear.

> [!ATTENTION]
>
> `makei build` will try to build all changes objects, or all objects on the first time it's run. Consider creating an Action for `OPT=*EVENTF BUILDLIB=&CURLIB /QOpenSys/pkgs/bin/makei compile &BASENAME` to compile specific objects.

## Developing on the local machine with ibmi-tobi

You may use TOBi as the deploy backend for Code for IBM i by providing a customized `.vscode/actions.json` inside your workspace. [Read more on how to create the actions](https://halcyon-tech.github.io/vscode-ibmi/#/?id=workspaces-amp-deployment)

1. Make sure `ibmi-tobi` is installed on the remote IBM i
2. Clone the project repository to your local machine and open it up in VS Code
3. Connect to a remote IBM i using Code for IBM i to run the builds. (You can still develop without it!)
4. Set your current schema to the library you want to build in. You can do this in the User Library List view.
5. In the IFS Browser:
   1. Create a new directory in your home directory for where the sources will be uploaded and compiled from
   2. Right click on the new directory and select 'Set Deploy Workspace Location'. This is where files from your local machine will be uploaded to and compiled from.
6. In your workspace, create a new file: `./.vscode/actions.json`. 
   * This is where Actions specific to this project belong.
   * This file should be checked into the repo so all developers share the same actions.

---

7. Inside of `actions.json`, place this JSON:

```json
[
  {
    "name": "Deploy & build all 🔨",
    "command": "OPT=*EVENTF BUILDLIB=&CURLIB /QOpenSys/pkgs/bin/makei build",
    "extensions": [
      "GLOBAL"
    ],
    "environment": "pase",
    "deployFirst": true
  }
]
```

Actions defined in your `actions.json` will show up with the other Actions when using the shortcut. This will:

   * Upload files to chosen deploy location (which was done in step 5)
   * Run the provided command (`makei build`)

---

8. Open the source code up that you want to compile
9. Use the Action, which will upload files & run the defined command
   * Shortcut to run an Action is Control / Command + E
   * You will see the Output in the IBM i Output channel.
   * If your current library and build library match, the errors (if any) should appear.
