from distutils.core import setup
import setup_translate


setup(name='enigma2-plugin-extensions-btdevicesmanager',
		version='1.0',
		author='SatDreamGr',
		package_dir={'Extensions.BTDevicesManager': 'src'},
		packages=['Extensions.BTDevicesManager'],
		package_data={'Extensions.BTDevicesManager': ['*.png']},
		description='Bluetooth Devices Manager',
		cmdclass=setup_translate.cmdclass,
	)
