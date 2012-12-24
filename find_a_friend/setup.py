from distutils.core import setup, Extension

setup(name="find_a_friend",
      version="0.0.1", 
      description="Make/Find a friend service for papuacom",
      author="Kurtis Heimerl",
      author_email="kheimerl@cs.berkeley.edu",
      url="http://tier.cs.berkeley.edu",
      packages=['vbts_faf'],
      license='BSD',
      scripts=[],
      install_requires=['libvbts'],
      data_files=[
        ("/usr/local/freeswitch/scripts",['scripts/find_a_friend.py']),
        ("/usr/local/freeswitch/scripts",['scripts/set_a_friend.py'])
        ]
      )
