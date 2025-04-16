import sys
from pysca import app
from pysca.device import PYPLC
import pygui.navbar as navbar
from concrete6 import concrete6

def whats_inside(*args):
    try:
        n = 0
        msg = '<table><tr><th align="left">КОМПОНЕНТ</th><th align="right">M</th></tr>'
        for arg in args:
            if arg>0:
                msg += f'<tr><td>{concrete6.containers[n].component}</td><td align="right">{arg:.0f}</td></tr>\n'
            n+=1
        msg+='</table>'
        return msg
    except:
        pass
    
    return "Here should be an tooltip"

def main():
    import argparse
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--device', action='store', type=str, default='192.168.2.10', help='IP address of the device')
    args.add_argument('--simulator', action='store_true', default=False, help='Same as --device 127.0.0.1')
    ns = args.parse_known_args()[0]
    if ns.simulator:
        ns.device = '127.0.0.1'
        import subprocess
        logic = subprocess.Popen(["python3", "src/krax.py"])
    
    dev = PYPLC(ns.device)
    app.devices['PLC'] = dev
    
    Home = app.window('ui/Home.ui',ctx={"whats_inside":whats_inside})
    navbar.append(Home)       
    navbar.tools(app.window('ui/Extensions.ui'))
    navbar.instance.show( )
    app.object(concrete6.instance)
    concrete6.setMainWindow(navbar.instance)
    concrete6.setContainerPanels( (Home.cpanel_1,Home.cpanel_2,Home.cpanel_3,Home.cpanel_4,Home.cpanel_5,Home.cpanel_6) )
    
    dev.start(100)
    app.start( ctx = globals() )
    dev.stop( )
    
    concrete6.save( )

    if ns.simulator:
        logic.terminate( )
        pass

if __name__=='__main__':
    main( )
    