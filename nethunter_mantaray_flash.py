import os
import subprocess as sp
import sys
import time


global windows
global ls
global grep
global unzip


class use:
    """
    General use-case class for error reporting and finding files
    """
################################################################################
    def __init__(self, e=0):
        self.e_code = { 0 : lambda : [print("[-] Please put all images/files into one directory labeled MantaNet."), sys.exit(0)],
                        1 : lambda : [print("[!] Please install Android Debugging Bridge (ADB) [!]\n"), sys.exit(1)],
                        2 : lambda : [print("[!] Please install Fastboot [!]\n"), sys.exit(1)],
                        3 : lambda : [print("[-] Please download the latest Nexus10 Mantaray Stock image\nand move the .zip to your MantaNet Folder"), sys.exit(1)],
                        4 : lambda : [print("[-] Please download the latest version of Kali nethunter\nand move the .zip to your Mantanet Folder"), sys.exit(1)],
                        5 : lambda : [print("[-] Please download the TWRP recovery .img you would like to use\n"), sys.exit(1)],
                        6 : lambda : [print("[-] Please download the SuperSu zip you would like to use")],
                        7 : lambda : [print("[-] No ADB device was detected.\n\t[*] Please make sure you have USB Debugging turned on\n[+] Can be found in the Devloper Options\n")] }


    def err(self, e):
        if e > -1:
            self.e_code[e]()


    def find(self, mn = 0):
        #Could send string but this keeps everything confined; less likely command injection
        what = {0 :"mantaray", 1 : "nethunter", 2 : "twrp", 3 : "Super"}
        #slightly redundant but provides some semblance of a check for the files
        prc = sp.Popen(["{}".format(ls), "MantaNet"], stdout=sp.PIPE)
        grp = sp.Popen((["{}".format(grep), "{}".format(what[mn])]), stdin=prc.stdout, stdout=sp.PIPE)
        prc.stdout.close()
        fn = grp.communicate()[0]
        grp.stdout.close()
        if fn is not None:
            return fn
        return None


    def checkifzip(self, phile):
        phile = phile
        if (phile.split(".")[-1]=="zip"):
            return True
        return False


    def uzip(self, phile):
        uz = lambda arg="",arg1="": (sp.Popen(["{}".format(unzip)], stdout=sp.PIPE) if arg == "" else sp.Popen(["{}".format(unzip), "{}".format(arg)], stdout=sp.PIPE)\
                                                                            if arg1 == "" else sp.Popen(["{}".format(unzip), "{}".format(arg1), "{}".format(arg2)], stdout=sp.PIPE))
        if self.checkifzip(phile):
            #Command injection Vulnerability
            uz("{}".format(phile))
            time.sleep(1)
            folder = phile.split("-")[:2]
            folder = '-'.join(folder)
            try:
                print("[*] Moving into unzipped folder {}".format(folder))
                os.chdir(folder)
            except:
                print("Unable to change working directory to unzipped file")
                sys.exit(1)
            print("[+] Current Working Directory is Now : {}".format(os.getcwd()))
            return
        print("File %s is not a .zip file" % phile)
        sys.exit(1)


################################################################################

class FastBoot:
    """
    Class that allows easy use of the fastboot command
    """
################################################################################
    def __init__(self, adb):
        self.fastboot = lambda arg1="",arg2="",arg3="": (sp.Popen(["fastboot"], stdout=sp.PIPE) if arg1 == "" else sp.Popen(["fastboot", "{}".format(arg1)], stdout=sp.PIPE)\
                                                                            if arg2 == "" else sp.Popen(["fastboot", "{}".format(arg1), "{}".format(arg2)], stdout=sp.PIPE)\
                                                                            if arg3 == "" else sp.Popen(["fastboot", "{}".format(arg1), "{}".format(arg2), "{}".format(arg3)], stdout=sp.PIPE))
        self.adb = adb

        self.sectors = ["recovery", "boot", "system", "data", "cache", "misc"]


    def wc(self):
        """
        No modification on returned value because fastboot returns 0 if no device is found
        """
        lc = sp.Popen(["wc", "-l"], stdin = self.fastboot("devices").stdout, stdout=sp.PIPE)
        return int(lc.communicate()[0])


    def BootLockControl(self, switch=0):
        """
        Function to Lock/Unlock BootLoader
        """
        adb = self.adb
        fastboot = self.fastboot
        cntrl = "unlock" if switch == 0 else "lock"
        while True:
            if (self.wc() > 0):
                break
        print("\n[+] Locking/Unlocking BootLoader via `oem (un)lock`")

        self.fastboot("oem", cntrl)
        time.sleep(3)
        fastboot("reboot")
        print("\n[+] Waiting for device...\n")
        while True:
            time.sleep(0.5)
            if ( adb.wc() >= 1):
                break


    def flashFile(self, phile, sector=0):
        """
        Flash an image to a particular partition on the android device
        The Sectors are hard-coded into this class
        """
        print("[+] Rebooting to Bootloader\n")
        fastboot = self.fastboot
        adb = self.adb
        adb.reboot(2)
        part = self.sectors[sector]
        while True:
            time.sleep(0.5)
            num_fb_devs = self.wc()
            #if multiple devices, prompt for which device
            if num_fb_devs == 1:
                break
        print("\t[+] Flashing {} image {}".format(part, phile))
        fastboot("flash", part, phile).communicate()[0]
        time.sleep(2)
        fastboot("reboot").communicate()[0]


    def bootimg(self, phile):
        self.fastboot("boot", phile)


################################################################################

class ADB:
    """
    Class to easily use the ADB program
    """
################################################################################
# Uses subprcess, Process Open, Popen, module to interact with ADB program.
    def __init__(self):
        # Lambda takes two optional arguments and determines if they are received.
        # Then builds the command, adding up to three arguments to the adb program
        self.adb = lambda arg0="",arg1="",arg2="": (sp.Popen(["adb"], stdout=sp.PIPE) if arg0 == "" else sp.Popen(["adb", "{}".format(arg0)], stdout=sp.PIPE)\
                                                                            if arg1 == "" else sp.Popen(["adb", "{}".format(arg0), "{}".format(arg1)], stdout=sp.PIPE)\
                                                                            if arg2 == "" else sp.Popen(["adb", "{}".format(arg0), "{}".format(arg1), "{}".format(arg2)], stdout=sp.PIPE))


    def wc(self):
        lc = sp.Popen(["wc", "-l"], stdin = self.adb("devices").stdout, stdout=sp.PIPE)
        num_devs = lc.communicate()[0]
        num_devs = int(num_devs) - 2 # 2 Extra \n are used, so we subtract them
            #print("Total # of ADB Devices {}".format(num_devs))
        return num_devs


    def waitfordev(self):
        while True:
            time.sleep(0.5)
            num_adb_devs = self.wc()
            #if multiple devices, prompt for which device
            if num_adb_devs == 1:
                break


    def devs(self):
        return self.adb("devices").communicate()[0]


    def get_dev(self, ln=2):
        gawk = sp.Popen(["gawk", "'BEGIN {RS="" ; FS=""} {print ${}}'".format(ln)], stdin = self.adb("devices").stdout)
        return gawk.communciate()[0]


    def reboot(self, arg=0):
        opts = {0 : "system", 1 : "recovery" , 2 : "bootloader" }
        try:
            self.adb("reboot", opts[arg]).communicate()[0]
        except:
            print("[!] Unable to boot into {} [!]".format(opts[arg]))


    def push(self, phile, dest):
        self.adb("push", phile, dest).communicate()[0]


################################################################################

class MantaNet:
    """
    Main class to step through the process
    """
################################################################################

    def __init__(self, u, files, dest):
        self.adb = ADB()
        self.fastboot = FastBoot(self.adb)
        self.u = u
        self.files = files
        self.dest = dest


    def dev_check(self):
        """
        Check the number of devices connected over ADB
        """
        num_devs = self.adb.wc()
        if (num_devs == 0):
            self.u.err(7)


    def unlockBoot(self):
        """
        Wrapper function for the BootLockControl in the FastBoot class
        """
        print("[+] Rebooting into BootLoader...")
        self.adb.reboot(2)
        time.sleep(1)
        self.fastboot.BootLockControl(0)


    def retryStockFlash(self):
        """
        Mildly Self-Explanatory
        """
        print("[-][-] Make sure the device is On with USB Debugging Enabled\n\t[-] As well as MTP disabled")
        if (input("Would you like to retry Flashing Stock? (y/n)") != "y"):
            print("\n\tExiting...\n")
            sys.exit(1)
        print("\n\tRetrying FlashStock")
        self.FlashStock()


    def FlashStock(self):
        """
        Simply calls the flashall script
        Default is .bat because I am on Windows
        """
        #check if adb device is connected
        ### NEED TO ADD "if more than one" prompt
        stock = self.files[1]
        self.u.uzip(stock)
        if self.adb.wc() == 0:
            print("[-] Waiting for ADB device... ")
            i = 0
            while i < 10:
                if (self.adb.wc() >= 1):
                    print("[+] Found Device\n")
                    break
                time.sleep(1)
                i += 1
            if i == 10:
                print("[!] No ADB device found after 10 seconds [!]")
                self.retryStockFlash(self)

        self.adb.reboot(2)
        time.sleep(2)
        if (sp.check_call(["flash-all.bat"]) == 0): #Obviously has to wait for check_call to return so no need to time delay after if statement
            os.chdir("..")
            print("[*] Working directory is now {}".format(os.getcwd()))
            print("[+] Please be patient while the Stock Image BootStraps itself to the HardWare\n\tThis could take some time...")
            time.sleep(120)
            print("[++] I swear, nothing is broken.\n\tIt has only been 2 minutes.")
            time.sleep(2)
            print("[*] I am going to go into a loop and wait for your device to boot back up.\n")
            print("[!!] Remember to Turn ON USB Debugging and Turn OFF MTP on your freshly Written OS [!!]")
            self.adb.waitfordev()
            return

        print("[!] Was unable to Flash the stock image using the default flash-all script [!]")
        self.retryFlashStock()


    def flashTwrp(self):
        """
        Flash the TWRP recovery image to the recovery sector
        """
        twrp_file = self.files[0]
        print("\n[+] Attempting to Flash TWRP recovery image....")
        self.fastboot.flashFile(twrp_file, 0)


    def BootTwrp(self):
        """
        Boot the Twrp img
        """
        twrp_file = self.files[0]
        self.fastboot.bootimg(twrp_file)


    def Root(self):
        self.adb.waitfordev()
        #push SuperSu zip file
        print("Pushing SuperSU zip file to your {} Folder".format(self.dest))
        supersu = self.files[2]
        dest = self.dest
        # Not sure if the program waits for the process to finish or simply\
        # continues with the process operating in the bg
        self.adb.push(supersu, dest)
        #reboot
        time.sleep(3)
        self.adb.reboot(2)
        print("You will now need to install the SuperSU zip file from the download folder after hitting 'Install' on the TWRP Menu")
        if (input("Press any button to start to push nethunter...")):
            return


    def Push_NetHunter(self):
        nethunter = self.files[3]
        dest = self.dest + "nethunter.zip"
        #push nethuter image
        time.sleep(2)
        while True:
            if self.adb.wc() >= 1:
                break
        #prompt user that device needs to be interacted with
        print("[+] Pushing Nethunter...")
        self.adb.push(nethunter, dest)
        time.sleep(3)
        print("Please Install the nethunter*.zip from your devices Download Folder via the TWRP Recovery Image")
        if (input("Press any button to reboot system and relock BootLoader...")):
            self.adb.waitfordev()
            self.adb.reboot(2)
            return


    def lockBoot(self):
        """
        Wrapper function for the BootLockControl in the FastBoot class
        """
        self.fastboot.BootLockControl(1)


    def close(self):
        #clean and close up
        print("Clean")
        pass

################################################################################

def checks(u):

#check adb install
    if not (lambda : sp.check_call("adb version")):
        u.err(1)

#check fastboot install
    if not (lambda : sp.check_call("fastboot")):
        u.err(2)

#check for mantaray image
    stock = u.find()
    if stock is None:
        u.err(3)

#check for nethunter image
    nethunter = u.find(1)
    if nethunter is None:
        u.err(4)

#Check for twrp recovery image
    twrp = u.find(2)
    if twrp is None:
        u.err(5)

#Check for SuperSu file
    supersu = u.find(3)
    if supersu is None:
        u.err(6)

    return twrp, stock, supersu, nethunter

def main(MN):
    MN.dev_check()
    #MN.unlockBoot()
    #MN.FlashStock()
    #MN.flashTwrp()
    MN.BootTwrp()
    MN.Root()
    MN.BootTwrp() # Second time because root requires reboot, nethunter install requires TWRP
    MN.Push_NetHunter()
    #MN.lockBoot()
    #MN.clean()

if __name__=="__main__":
    """
    Preamble to calling Main function
    """
    windows = False
    platform = sys.platform
    ls = 'ls'
    grep = 'grep'
    unzip = 'unzip'
    dest = "/mnt/sdcard/Download/"
    files = []
    u = use()
    #if platform is "win32" or "win64" :
    #    windows = True
    if windows:
        ls = "dir"
        grep = "find"
        unzip = "expand"
    roughfiles = checks(u)
    for file in roughfiles:
        files.append(file.__str__().replace("(", "").replace("\\n\'","").replace(")", "").replace("b'", ""))

    os.chdir("MantaNet")
    MN = MantaNet(u, files, dest)
    main(MN)
