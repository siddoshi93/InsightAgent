#!/bin/python
import os
import pwd
import sys
import subprocess
requiredPackagesinHost = ["requests"]
requiredPackagesDeploy = ["requests", "paramiko"] # Required packages for the machine from where the deployment script is run

'''
This script checks for required packages and installs using pip
'''

class checkpackages:

    def checkRequirementsFile(self):
        if(os.path.isfile(os.path.join(homepath,"deployment","requirements")) == False):
            with open(os.path.join(homepath,"deployment", "requirements"),"w") as req:
                for package in requiredPackagesinHost:
                    print package
                    req.write(package)
                    req.write("\n")

    def installpip(self):
        try:
            import pip
        except ImportError as e:
            # Install pip if not found
            proc = subprocess.Popen(["sudo python " + os.path.join(homepath, "deployment", "get-pip.py")], cwd=homepath,
                                    stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            try:
                import pip
            except ImportError as e:
                print "Dependencies are missing. Please install the dependencies as stated in README"
                sys.exit()

    def installVirtualenv(self):
        pyVersion = sys.version
        versionElements = pyVersion.split(" ")[0].split(".")
        version = versionElements[0] + "." + versionElements[1]
        command = "sudo chown -R " + user + " /home/" + user + "/.local"
        proc = subprocess.Popen([command], cwd=homepath, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")
        (out, err) = proc.communicate()
        command = "pip install -U --force-reinstall --user virtualenv\n \
                python  /home/" + user + "/.local/lib/python" + version + "/site-packages/virtualenv.py pyenv\n \
                source pyenv/bin/activate\n \
                pip install -r deployment/requirements\n"
        proc = subprocess.Popen([command], cwd=homepath, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")
        (out, err) = proc.communicate()

    def installPackagesForDeployment(self):
        self.installpip()
        import pip
        installed_packages = pip.get_installed_distributions()
        flat_installed_packages = [package.project_name for package in installed_packages]
        for eachpackage in requiredPackagesDeploy:
            if eachpackage in flat_installed_packages:
                print "%s already Installed" % eachpackage
            else:
                print "%s not found. Installing..." % eachpackage
        try:
            pip.main(['install', '-q', eachpackage])
        except:
            print "Unable to install %s using pip. Please install the dependencies as stated in README" % eachpackage

if __name__ == '__main__':
    homepath = os.getcwd()
    user = pwd.getpwuid(os.geteuid()).pw_name
    checkReq = checkpackages()
    checkReq.checkRequirementsFile()
    checkReq.installpip()
    checkReq.installVirtualenv()

