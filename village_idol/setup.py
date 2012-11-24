from distutils.core import setup, Extension

setup(name="village_idol",
      version="0.0.1", 
      description="The village idol app for papua's VBTS deployment",
      author="Kurtis Heimerl",
      author_email="kheimerl@cs.berkeley.edu",
      url="http://tier.cs.berkeley.edu",
      license='BSD',
      scripts=[],
      install_requires=['python-messaging', 'libvbts'],
      data_files=[
        ("/usr/local/freeswitch/scripts",['scripts/village_idol_record.py']),
        ("/usr/local/freeswitch/sounds", ['sounds/intro.wav'])

        ]
      )
