#====================================================
# Bluetooth Devices Manager - basic version
# Version date - 20.11.2014
# Coding by a4tech - darezik@gmail.com (oe-alliance)
#
# Modified by satdreamgr using only bluetool  
#
# requierments: bluez5 python-bluetool
# Some Kernel modules for support HID devices
# 
# For example: 
# kernel-module-hid-a4tech 
# kernel-module-hid-apple 
# kernel-module-hid-appleir 
# kernel-module-hid-belkin 
# kernel-module-hid-magicmouse 
# kernel-module-hid-microsoft 
# kernel-module-hid-wacom 
#====================================================

from . import _

from Plugins.Plugin import PluginDescriptor
from enigma import eTimer, eConsoleAppContainer

from Screens.Screen import Screen

from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Tools.HardwareInfo import HardwareInfo

from bluetool import Bluetooth

import os

class BluetoothDevicesManager(Screen):
	skin = """
		<screen name="BluetoothDevicesManager" position="center,center" size="700,450" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,10" size="35,25" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="180,10" size="35,25" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="370,10" size="35,25" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="550,10" size="35,25" alphatest="on" />
		<eLabel name="" position="0,40" size="700,1" zPosition="2" backgroundColor="#ffffff" />		
		<eLabel name="" position="0,355" size="700,1" zPosition="2" backgroundColor="#ffffff" />			
		<widget name="key_red" position="45,10" zPosition="1" size="140,22" font="Regular;22" halign="left" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
		<widget name="key_green" position="215,10" zPosition="1" size="140,22" font="Regular;22" halign="left" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
		<widget name="key_yellow" position="405,10" zPosition="1" size="140,22" font="Regular;22" halign="left" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff" transparent="1" />
		<widget name="key_blue" position="585,10" zPosition="1" size="140,22" font="Regular;22" halign="left" valign="center" backgroundColor="#18188b" foregroundColor="#ffffff" transparent="1" />
		<widget name="devicelist" position="10,50" size="690,300" foregroundColor="#ffffff" zPosition="10" scrollbarMode="showOnDemand" transparent="1"/>
		<widget name="ConnStatus" position="10,365" size="690,80" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Bluetooth Devices Manager"))

		# initialize bluetooh
		self.bluetool = Bluetooth()

		self["actions"] = ActionMap(["OkCancelActions","WizardActions", "ColorActions", "SetupActions", "NumberActions", "MenuActions"], {
			"ok": self.keyOK,
			"cancel": self.keyCancel,
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
		}, -1)

		self["ConnStatus"] = Label()
		self["key_red"] = Label(_("Scan"))
		self["key_green"] = Label(_("Connect"))
		self["key_yellow"] = Label(_("Disconnect"))
		self["key_blue"] = Label(_("Paired"))

		self.devicelist = []
		self["devicelist"] = MenuList(self.devicelist)

		self.scan = eTimer()
		self.scan.callback.append(self.DevicesToPair)
		self.scanning = False

		self.keyRed()

	def keyRed(self):
		print "[BluetoothManager] keyRed"

		self.showConnections()

		if self.scanning:
			return
 
		self.setTitle(_("Scanning..."))

		self.devicelist = []
		self.devicelist.append((_("Scanning for devices..."), None))
		self["devicelist"].setList(self.devicelist)

		# add background task for scanning
		self.bluetool.start_scanning()
		self.scan.start(10000)
		self.scanning = True

	def DevicesToPair(self):
		print "[BluetoothManager] DevicesToPair"
		self.setTitle(_("Scan Results..."))
		self.scan.stop()
		self.scanning = False

		self.devicelist = []
		self.devicelist.append((_("MAC:\t\tDevice name:"), None))

		devices_to_pair = self.bluetool.get_devices_to_pair()
		for d in devices_to_pair:
			self.devicelist.append((d['mac_address'] + "\t" + d['name'], d['mac_address']))
		if not len(devices_to_pair):
			self["ConnStatus"].setText(_("There are no devices to pair"))

		self["devicelist"].setList(self.devicelist)

	def showConnections(self):
		print "[BluetoothManager] showConnections"
		connected_devices = ",".join([d['name'] for d in self.bluetool.get_connected_devices()])
		if not connected_devices:
			self["ConnStatus"].setText(_("Not connected to any device"))
		else:
			self["ConnStatus"].setText(_("Connected to %s") % connected_devices)

	def keyGreen(self):
		print "[BluetoothManager] keyGreen"

		selectedItem = self["devicelist"].getCurrent()
		if selectedItem is None or selectedItem[1] is None:
			return
		device = selectedItem[1]

		if device in [d['mac_address'] for d in self.bluetool.get_connected_devices()]:
			return

		if device in [d['mac_address'] for d in self.bluetool.get_paired_devices()]:
			if self.bluetool.connect(device):
				self.showConnections()
			else:
				self["ConnStatus"].setText(_("Failed to connect %s") % device)
			return

		msg = _("Trying to pair with:") + " " + device
		self["ConnStatus"].setText(msg)

		if self.bluetool.pair(device):
			self["ConnStatus"].setText(_("Sucessfuly paired %s") % device)
			self.bluetool.trust(device)
			self.bluetool.connect(device)
			self.DevicesToPair()
			self.showConnections()
		else:
			self["ConnStatus"].setText(_("Fail to pair %s") % device)

	def keyYellow(self):
		print "[BluetoothManager] keyBlue"

		selectedItem = self["devicelist"].getCurrent()
		if selectedItem is None or selectedItem[1] is None:
			return
		device = selectedItem[1]

		if self.bluetool.remove(device):
			self["ConnStatus"].setText(_("Sucessfuly removed %s") % device)
			self.keyBlue()
		else:
			self["ConnStatus"].setText(_("Fail to remove %s") % device)

	def keyBlue(self):
		print "[BluetoothManager] keyBlue"
		self.setTitle(_("Paired Devices"))

		self.devicelist = []
		self.devicelist.append((_("MAC:\t\tDevice name:"), None))

		paired_devices = self.bluetool.get_paired_devices()
		for d in paired_devices:
			self.devicelist.append((d['mac_address'] + "\t" + d['name'], d['mac_address']))
		if not len(paired_devices):
			self["ConnStatus"].setText(_("Not paired to any device"))
		self["devicelist"].setList(self.devicelist)

	def keyCancel(self):
		print "[BluetoothManager] keyCancel"
		self.close()

	def keyOK(self):
		print "[BluetoothManager] keyOK"
		self.keyGreen()

	def setListOnView(self):
		return self.devicelist

def main(session, **kwargs):
	session.open(BluetoothDevicesManager)

def autostart(reason, **kwargs):
	if reason == 0:
		# A noteworthy new feature is the ability to configure bluetoothd to automatically enable (power on) all new adapters.
		# One use of this is to replace unreliable "hciconfig hci0 up" commands that some distributions use in their init/udev scripts.
		# The feature can be enabled by having AutoEnable=true under the [Policy] section of /etc/bluetooth/main.conf.
		if not os.path.exists("/etc/bluetooth/main.conf"):
			open("/etc/bluetooth/main.conf", "w").write("[Policy]\nAutoEnable=true\n")
			eConsoleAppContainer().execute("/etc/init.d/bluetooth restart")
		cmd = None
		if HardwareInfo().get_device_model() in ("osmega"):
			cmd = "hciattach ttyS1 rtk_h5 && /etc/init.d/bluetooth restart"
		if HardwareInfo().get_device_model() in ("osmini", "osminiplus", "osnino", "osninoplus", "osninopro"):
			cmd = "hciattach ttyS2 rtk_h5 && /etc/init.d/bluetooth restart"
		if cmd:
			print "[BluetoothManager] autostart: %s" % cmd
			eConsoleAppContainer().execute(cmd)

def Plugins(**kwargs):
	return [PluginDescriptor(where=[PluginDescriptor.WHERE_AUTOSTART], fnc=autostart),
		PluginDescriptor(name=_("Bluetooth Devices Manager"),
		description=_("Manage your bluetooth devices"), icon="plugin.png", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]

